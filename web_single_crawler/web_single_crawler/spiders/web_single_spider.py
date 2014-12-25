# coding: UTF-8

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy import log
from scrapy.http import Request
import hashlib
import simplejson as json
import time

from web_single_crawler.items import NewsItem

import redis
import MySQLdb
import sys

# reload(sys)
# sys.setdefaultencoding("utf-8")
class WebSingleSpider(Spider):
    target_list = []
    name = u'webSingle'
    allowed_domains = []
    start_urls = []
    def nextTarget(self,target_id):
        try:
            self.conn = MySQLdb.connect(host="localhost", user="webmoudel", passwd="newsMetro01", db="newsmetro", port=3306, charset="utf8")
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

        cur = self.conn.cursor()
        cur.execute('select * from target_point where id = %s and isRss=false;',target_id)
        self.conn.commit()
        for t in cur:
            print t[2]
            yield {'id': t[0], 'url': t[3], 'xpath': t[5], 'regex': t[6],'md5': t[7], 'status': t[9]}
        cur.close()

    def __init__(self,target_id):
        self.target_id = target_id
        self.target_list = self.nextTarget(target_id)
        self.current_target = ''
        self.redis_conn = redis.Redis(host='127.0.0.1', port=6379)
        return

    def start_requests(self):
        self.current_target = self.target_list.next()
        start_url = self.current_target['url']
        yield Request(start_url, dont_filter=True)

    def parse(self, response):
        res_body = response._get_body()
        md5 = hashlib.md5(res_body).hexdigest()
        #md5 = ''
        sel = Selector(response)
        news_list = sel.xpath(self.current_target['xpath']+'//a')
        items = []

        for news in news_list:
            item = NewsItem()

            text = news.xpath('text()').extract()[0]
            link = news.xpath('@href').extract()[0]
            item['text'] = text.encode('utf-8')
            item['href'] = link

            items.append(item)
            #log.msg("Appending item...", level='INFO')

       	log.msg("Appending done.", level='INFO')
        self.updateInfo(md5, self.current_target, items)
        yield items

        self.current_target = self.target_list.next()
        yield Request(self.current_target['url'], dont_filter=True)


    def updateInfo(self, md5, current_target,items):
        pValue = (md5, self.current_target['id'])
        cur = self.conn.cursor()
        cur.execute('update target_point set md5 = %s where id=%s', pValue)
        self.conn.commit()

        cur = self.conn.cursor()
        cur.execute('select count(*) from target_mapping as tm where tm.target_id=%s', current_target['id'])
        count = cur.fetchone()[0]

        if count == 1:
            jsonStr = self.transJson(items)
            mValue = (jsonStr , time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), current_target['id'])
            cur.execute('update target_mapping set items = %s , update_time=%s where target_id=%s', mValue)
        elif count==0:
            jsonStr = self.transJson(items)
            mValue = (current_target['id'], jsonStr , time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
            cur.execute('insert into target_mapping(target_id,items,update_time) values(%s,%s,%s)', mValue)
        self.redis_conn.set('target:md5:'+str(current_target['id']), md5)
        self.conn.commit()
        return

    def transJson(self,items):
        str = '['
        for i in items:
            str += '{\"text\":\"'+i['text']+'\",\"href\":\"'+i['href']+'\"},'
        str = str[0:-1]
        str += ']'
        return str

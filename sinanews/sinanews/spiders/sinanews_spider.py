# coding: UTF-8

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy import log
from scrapy.http import Request
import hashlib
import simplejson as json
import time
import re

from sinanews.items import SinanewsItem

import redis
import MySQLdb
import sys

# reload(sys)
# sys.setdefaultencoding("utf-8")
class SinanewsSpider(Spider):
    handle_httpstatus_list = [302,403,404,500]
    target_list = []
    name = u'sinanews'
    allowed_domains = []
    start_urls = []
    hrefRex = re.compile(r'(https?://.*?/)')
    def nextTarget(self):
        try:
            self.conn = MySQLdb.connect(host="localhost", user="root", passwd="root", db="newsmetro", port=3306, charset="utf8")
        except MySQLdb.Error,e:
            print "Mysql Error %d: %s" % (e.args[0], e.args[1])

        cur = self.conn.cursor()
        cur.execute('select * from target_point where isRss=false;')
        self.conn.commit()
        for t in cur:
            print t[2]
            yield {'id': t[0], 'url': t[3], 'xpath': t[5], 'regex': t[6],'md5': t[7], 'status': t[9]}
        cur.close()

    def __init__(self):
        self.target_list = self.nextTarget()
        self.current_target = ''
        self.redis_conn = redis.Redis(host='127.0.0.1', port=6379)
        return

    def start_requests(self):
        self.current_target = self.target_list.next()
        start_url = self.current_target['url']
        yield Request(start_url, dont_filter=True)

    def parse(self, response):
        if response.status != 200 :
            log.msg(self.current_target['url']+"crawl failure! status:"+str(response.status))
            self.current_target = self.target_list.next()
            return Request(self.current_target['url'], dont_filter=True)
        res_body = response._get_body()
        md5 = hashlib.md5(res_body).hexdigest()
        #md5 = ''
        sel = Selector(response)
        news_list = sel.xpath(self.current_target['xpath']+'//a')
        items = []

        for news in news_list:
            item = SinanewsItem()
            names =  news.xpath('text()').extract()
            if len(names) == 0:
                continue
            name = news.xpath('text()').extract()[0]
            link = news.xpath('@href').extract()[0]
            item['text'] = name.encode('utf-8')
            item['href'] = link.strip()
            print name.encode('utf-8')
            items.append(item)
            #log.msg("Appending item...", level='INFO')

       	log.msg("Appending done.", level='INFO')
        self.updateInfo(md5, self.current_target, items)

        self.current_target = self.target_list.next()
        return Request(self.current_target['url'], dont_filter=True)


    def updateInfo(self, md5, current_target,items):
        pValue = (md5, self.current_target['id'])
        cur = self.conn.cursor()
        cur.execute('update target_point set md5 = %s where id=%s', pValue)
        self.conn.commit()

        cur = self.conn.cursor()
        cur.execute('select count(*) from target_mapping as tm where tm.target_id=%s', (current_target['id'],))
        count = cur.fetchone()[0]

        jsonStr = self.transJson(items,current_target)
        jsonMd5 = hashlib.md5(jsonStr).hexdigest()
        if count == 1:
            mValue = (jsonStr , jsonMd5 , time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())), current_target['id'])
            cur.execute('update target_mapping set items = %s , md5 = %s , update_time=%s where target_id=%s', mValue)
        elif count==0:
            mValue = (current_target['id'], jsonStr , jsonMd5 , time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
            cur.execute('insert into target_mapping(target_id,items,md5,update_time) values(%s,%s,%s,%s)', mValue)
        self.redis_conn.set('target:md5:'+str(current_target['id']), md5)
        self.conn.commit()
        return

    def transJson(self,items,target):
        prefix = self.hrefRex.search(target['url']).group(1)
        linkMap = {}

        for i in items:
            if i['text']==None or i['text'].strip()=="" or i['href']==None or i['href'].strip()=="" :
                continue
            
            if i['href'].find('http://') == -1 :
                i['href'] = prefix + i['href']

            if not linkMap.has_key(i['href']) or len(linkMap[i['href']]) < len(i['text']):
                linkMap[i['href']] = i['text'].replace('\"','\\\"').strip()
        
        str = '['
        for i in items:
            if linkMap[i['href']]==None :
                continue
            str += '{\"text\":\"'+linkMap[i['href']]+'\",\"href\":\"'+i['href']+'\"},'
            linkMap[i['href']] = None
        
        str = str[0:-1]

        str += ']'
        return str
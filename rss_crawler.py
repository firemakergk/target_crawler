# coding: UTF-8

import hashlib
import simplejson as json
import time

import MySQLdb
import sys
import feedparser

# reload(sys)
# sys.setdefaultencoding("utf-8")
class RssCrawler:

    def transJson(self,rss):
        str = '{'
        str += '\"title\":\"'+rss.feed.title.replace('\"','\\\"')+'\",\"link\":\"'+rss.feed.link.replace('\"','\\\"')+'\",\"subtitle\":\"\",'
        str += '\"items\":['
        for i in rss.entries:
            str += '{\"text\":\"'+i['title'].replace('\"','\\\"')+'\",\"href\":\"'+i['link'].replace('\"','\\\"')+'\"},'
        str = str[0:-1]
        str += ']}'
        return str

    def crawlRss(self):
        try:
            self.conn = MySQLdb.connect(host="localhost", user="webmoudel", passwd="newsMetro01", db="newsmetro", port=3306, charset="utf8")
        except MySQLdb.Error,e:
            sys.stderr.write("Mysql Error %d: %s" % (e.args[0], e.args[1]))
        cur = self.conn.cursor()
        cur.execute('select * from target_point where isRss=true;')
        self.conn.commit()
        for t in cur:
            #yield {'id': t[0], 'url': t[3], 'xpath': t[5], 'regex': t[6],'md5': t[7], 'status': t[9]}
            rss = feedparser.parse(t[3])
            rssJson = self.transJson(rss)
            dataVal = (t[0], rssJson , time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
            cur1 = self.conn.cursor()
            cur1.execute('select count(*) from target_mapping where target_id = %s',t[0])
            count = cur1.fetchone()
            cur1.close()
            if count > 0:
                self.conn.cursor().execute('update target_mapping set items=%s,update_time=%s where target_id=%s', (rssJson,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),t[0]))
            else:
                self.conn.cursor().execute('insert into target_mapping(target_id,items,update_time) values(%s,%s,%s)', dataVal)
        cur.close()


RssCrawler().crawlRss()
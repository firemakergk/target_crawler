# coding: UTF-8

import hashlib
import simplejson as json
import time

import MySQLdb
import sys
import getopt
import feedparser

# reload(sys)
# sys.setdefaultencoding("utf-8")
class RssSingleCrawler:

    def transJson(self,rss):
        str = '{'
        str += '\"title\":\"'+rss.feed.title.replace('\"','\\\"')+'\",\"link\":\"'+rss.feed.link.replace('\"','\\\"')+'\",\"subtitle\":\"\",'
        str += '\"items\":['
        for i in rss.entries:
            str += '{\"text\":\"'+i['title'].replace('\"','\\\"')+'\",\"href\":\"'+i['link'].replace('\"','\\\"')+'\"},'
        str = str[0:-1]
        str += ']}'
        return str

    def crawlRssByTargetId(self, target_id):
        flag = 0
        try:
            self.conn = MySQLdb.connect(host="localhost", user="webmoudel", passwd="newsMetro01", db="newsmetro", port=3306, charset="utf8")
            cur = self.conn.cursor()
            cur.execute('select * from target_point where id = %s and isRss=true;', target_id)

            t = cur.fetchone()
            rss = feedparser.parse(t[3])
            rss_json = self.transJson(rss)

            cur1 = self.conn.cursor()
            cur1.execute('select count(*) from target_mapping where target_id = %s', t[0])
            count = cur1.fetchone()
            cur1.close()
            if count > 0:
                self.conn.cursor().execute('update target_mapping set items=%s,update_time=%s where target_id=%s', (rss_json,time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), t[0]))
            else:
                data_val = (t[0], rss_json, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
                self.conn.cursor().execute('insert into target_mapping(target_id,items,update_time) values(%s,%s,%s)', data_val)
            cur.close()
            self.conn.commit()
        except MySQLdb.Error, e1:
            flag = 1
            print "Mysql Error %d: %s" % (e1.args[0], e1.args[1])
        except Exception:
            flag = 2
        return flag;

    def crawlRssByUrl(self, url):
        flag = 0
        try:
            rss = feedparser.parse(url)
            rss_json = self.transJson(rss)
        except Exception:
            flag = 2
        if flag==0 :
            return rss_json
        else:
            return flag


shortargs = ''
longargs = ['target_id=', 'url=']
opts, args = getopt.getopt( sys.argv[1:], shortargs, longargs)

for t in opts:
    if t[0]=="--target_id":
        target_id = t[1]
    if t[0]=="--url":
        url = t[1]

crawler = RssSingleCrawler()
if target_id is not None:
    crawler.crawlRssByTargetId(target_id)
elif url is not None:
    print crawler.crawlRssByUrl(url)
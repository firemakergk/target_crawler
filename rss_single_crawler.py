# coding: UTF-8

import hashlib
import simplejson as json
import time

import MySQLdb
import sys
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

    def crawlRss(self, target_id):
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

RssSingleCrawler().crawlRss(sys.argv[1])
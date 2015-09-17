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
        # str = '{'
        # str += '\"title\":\"'+rss.feed.title.encode('utf-8').replace('\"','\\\"')+'\",\"link\":\"'+rss.feed.link.encode('utf-8').replace('\"','\\\"')+'\",\"subtitle\":\"\",'
        str = '['
        print rss.feed.title.encode('utf-8').replace('\"','\\\"')
        for i in rss.entries:
            str += '{\"text\":\"'+i['title'].encode('utf-8').replace('\"','\\\"')+'\",\"href\":\"'+i['link'].encode('utf-8').replace('\"','\\\"')+'\"},'
        str = str[0:-1]
        str += ']'
        return str

    def crawlRss(self):
        try:
            self.conn = MySQLdb.connect(host="localhost", user="root", passwd="root", db="newsmetro", port=3306, charset="utf8")
        except MySQLdb.Error,e:
            sys.stderr.write("Mysql Error %d: %s" % (e.args[0], e.args[1]))
        cur = self.conn.cursor()
        cur.execute('select * from target where type=2;')
        self.conn.commit()
        for t in cur:
            #yield {'id': t[0], 'url': t[3], 'xpath': t[5], 'regex': t[6],'md5': t[7], 'status': t[9]}
            print '--------crawling '+t[4] + '---------'
            rss = feedparser.parse(t[4])
            rssJson = self.transJson(rss)
            jsonMd5 = hashlib.md5(rssJson).hexdigest()
            dataVal = (t[0], rssJson , jsonMd5, time.time()*1000)
            cur1 = self.conn.cursor()
            cur1.execute('select count(*) from target_mapping where target_id = %s',(t[0],))
            count = cur1.fetchone()
            cur1.close()
            if count[0] > 0:
                self.conn.cursor().execute('update target_mapping set items=%s,md5=%s,update_time=%s where target_id=%s', (rssJson,jsonMd5,time.time()*1000,t[0]))
            else:
                self.conn.cursor().execute('insert into target_mapping(target_id,items,md5,update_time) values(%s,%s,%s,%s)', dataVal)
                
            for i in rss.entries:
                sql = ("select n.id as id from news as n where n.link='%s'") % (i['title'].encode('utf-8').replace('\"','\\\"'))
                newsId = cur.execute(sql)
                if newsId!=None and newsId!=0:
                    cur.execute('update news as n set n.title = %s,n.publish_time = %s where n.id=%s', (i['title'].encode('utf-8').replace('\"','\\\"'),time.time()*1000,newsId))
                else:
                    cur.execute("insert into news(target_id,title,link,status,publish_time,create_time) \
                        values(%s,%s,%s,%s,%s,%s)",(t[0],i['title'].encode('utf-8').replace('\"','\\\"'),i['link'].encode('utf-8').replace('\"','\\\"'),1,time.time()*1000,time.time()*1000))

        cur.close()


RssCrawler().crawlRss()

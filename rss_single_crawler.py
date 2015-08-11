# coding: UTF-8

import hashlib
import simplejson as json
import time

import MySQLdb
import sys
import getopt
import feedparser

reload(sys)
sys.setdefaultencoding("utf-8")
class RssSingleCrawler:

    def transJson(self,rss):
        str = '{'
        str += '\"title\":\"'+rss.feed.title.replace('\"','\\\"')+'\",\"link\":\"'+rss.feed.link.replace('\"','\\\"')+'\",\"subtitle\":\"\",'+'\"isSuccess\":true,'
        str += '\"itemList\":['
        for i in rss.entries:
            str += '{\"text\":\"'+i['title'].replace('\"','\\\"')+'\",\"href\":\"'+i['link'].replace('\"','\\\"')+'\"},'
        str = str[0:-1]
        str += ']}'
        return str

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
longargs = ['url=']
opts, args = getopt.getopt( sys.argv[1:], shortargs, longargs)

target_id = None
url = None
for t in opts:
    if t[0]=="--url":
        url = t[1]

crawler = RssSingleCrawler()
if url is not None:
    sys.stdout.write(crawler.crawlRssByUrl(url))

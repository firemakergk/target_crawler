# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import codecs
import MySQLdb

class SinanewsPipeline(object):

    def __init__(self):
        self.file = codecs.open('sina_news_data_utf8.json','wb',encoding='utf-8')


    def open_spider(self,spider):
        # try:
        #     self.conn=MySQLdb.connect(host='localhost',user='root',passwd='root',db='newsmetro',port=3306)
        # except MySQLdb.Error,e:
        #     print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        pass
    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + '\n'
        self.file.write(line.decode("unicode_escape"))
        ##values = [line]
        # cur= self.conn.cursor()
        # cur.execute('insert into `target_mapping`(target_id, items, update_time) values(%d,%s,from_unixtime(unix_timestamp()))',)
        # self.conn.commit()
        # cur.close()
        return item

    def close_spider(self,spider):
        # try:
        #     self.conn.close()
        # except MySQLdb.Error,e:
        #     print "Mysql Error %d: %s" % (e.args[0], e.args[1])
        pass
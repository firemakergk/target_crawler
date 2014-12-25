# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import codecs
import MySQLdb

class WebSinglePipeline(object):

    def __init__(self):
        self.file = codecs.open('web_single_crawler_data_utf8.json','wb',encoding='utf-8')


    def open_spider(self,spider):
        pass

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + '\n'
        self.file.write(line.decode("unicode_escape"))
        return item

    def close_spider(self,spider):
        pass
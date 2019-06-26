# -*- coding: utf-8 -*-
import pymysql
from scrapy.utils.project import get_project_settings
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class LawPipeline(object):

    def __init__(self):
        self.settings = get_project_settings()
        self.connect = pymysql.connect(
            host=self.settings['MYSQL_HOST'],
            db=self.settings['MYSQL_DBNAME'],
            user=self.settings['MYSQL_USER'],
            passwd=self.settings['MYSQL_PASSWD'],
            charset=self.settings['MYSQL_CHARSET'],
            use_unicode=True
        )
        self.cursor = self.connect.cursor()

    def process_item(self, item, spider):
        sql = 'insert ignore into law_scrapy.web_lawnature(title,doc, url) values(%s,%s,%s)'
        self.cursor.execute(sql, (item['title'], item['doc'], item['url']))
        self.connect.commit()

    def close_spider(self, spider):
        self.cursor.close()
        self.connect.close()

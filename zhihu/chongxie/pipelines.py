# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo


class ZhihuspiderPipeline(object):

    def __init__(self):
        client = pymongo.MongoClient('123.207.120.115',27017)
        scrapy_db = client['admin']  # 创建数据库
        scrapy_db.authenticate('zhihu','123456')#账号，密码
        self.coll = scrapy_db['zhihu_collections']      # 创建数据库中的表格
        print('正在白村')
        # client = pymongo.MongoClient('123.', 27017)
        # scrapy_db = client['tenct_news']  # 创建数据库
        # self.coll = scrapy_db['zhihu_collections']  # 创建数据库中的表格

    def process_item(self, item, spider):
        c = self.coll.find({"answer_id": item["answer_id"]}).count()
        print(c)
        # 如果没有值则插入
        if c == 0:
            self.coll.insert_one(dict(item))
        return item

    def close_spider(self, spider):
        pass

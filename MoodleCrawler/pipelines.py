# -*- coding: utf-8 -*-
import sqlalchemy
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from scrapy.exceptions import DropItem


class MongoPipeline(object):
    collection_name = 'course'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db[self.collection_name]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        cursor = self.collection.find()
        existed = [x for x in cursor]
        existed_keys = [x['key'] for x in existed]
        if item:
            # new course: insert directly
            if item['key'] not in existed_keys:
                self.collection.insert_one(dict(item))

            else:
                same = True
                # TODO if not, check every item

                if same:
                    raise DropItem("%s existed" % item['name'])

                # TODO if changed, delete the former one and insert new
                else:
                    pass
        else:
            print('wrong')
        return item

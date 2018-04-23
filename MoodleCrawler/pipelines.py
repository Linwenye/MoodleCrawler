# -*- coding: utf-8 -*-
import sqlalchemy
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from scrapy.exceptions import DropItem
from MoodleCrawler.mail import send_mail
from . import config


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
        self.client['admin'].authenticate(config.MONGO_USER, config.MONGO_PASSWORD)
        self.collection = self.db[self.collection_name]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        cursor = self.collection.find({'key': item['key']})
        existed = [x for x in cursor]
        if item:
            # new course: insert directly
            if not existed:
                print('insert new one', item['name'])
                self.collection.insert_one(dict(item))

            else:
                existed = existed[0]
                if item['children'] == existed['children']:
                    raise DropItem("%s existed" % item['name'])

                else:
                    mail_body = '课程 ' + item['name'] + ' 有了新的动态：'
                    for sub_item1, sub_item2 in zip(item['children'], existed['children']):
                        if not sub_item1 == sub_item2:
                            list1 = sub_item1['children']
                            list2 = sub_item2['children']

                            for tt in list1:
                                if tt not in list2:
                                    new_message = "- 新的" + sub_item2['name'] + ': ' + tt['name'] + '   链接：' + tt['link']
                                    mail_body = mail_body + '\n' + new_message
                                    print(new_message)

                    # if changed, delete the former one and insert new
                    self.collection.delete_one({'key': item['key']})
                    self.collection.insert_one(dict(item))

                    # send the email to inform
                    send_mail("Moodle Update", mail_body)

        else:
            print('wrong')
        return item

# -*- coding: utf-8 -*-
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from scrapy.exceptions import DropItem
from MoodleCrawler import mail
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
        self.exist_courses = list(self.collection.find())

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):

        existed = None
        for cc in self.exist_courses:
            if cc['key'] == item['key']:
                existed = cc
        if item:
            # new course: insert directly
            if not existed:
                print('insert new one', item['name'])
                del item['email']
                self.collection.insert_one(dict(item))
                # ! update the cache
                self.exist_courses.append(dict(item))

            else:
                if item['children'] == existed['children']:
                    raise DropItem("%s existed" % item['name'])

                else:
                    mail_body = '课程 ' + item['name'] + ' 有了新的动态：'
                    new_message = None
                    for sub_new in item['children']:

                        sub_exist = None
                        for query_item in existed['children']:
                            if sub_new['name'] == query_item['name']:
                                sub_exist = query_item
                        if not sub_new == sub_exist:
                            list_new = sub_new['children']
                            if sub_exist:
                                list_exist = sub_exist['children']
                            else:
                                list_exist = []
                            for tt in list_new:
                                if tt not in list_exist:
                                    new_message = "- 新的" + sub_new['name'] + ': ' + tt['name'] + '   链接：' + tt['link']
                                    mail_body = mail_body + '\n' + new_message
                                    # print(new_message)

                    # send the email to inform
                    if new_message:
                        mail.send_mail("Moodle Update", item['email'], item['key'], mail_body)

                    # if changed, delete the former one and insert new
                    self.collection.delete_one({'key': item['key']})
                    del item['email']
                    self.collection.insert_one(dict(item))

        else:
            print('wrong')
        return item

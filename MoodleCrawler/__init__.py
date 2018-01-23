import pymongo
from pprint import pprint

db = pymongo.MongoClient().moodle
collection = db.course
cursor = collection.find()
existed = [x for x in cursor]
if '需求工程' in [y['name'] for y in existed]:
    print('yes')

import scrapy
from scrapy.utils.response import open_in_browser
from scrapy.http import Request, FormRequest
import re
from pprint import pprint
import json
from MoodleCrawler.items import Course
from MoodleCrawler.items import CourseItem
from scrapy.loader import ItemLoader
from MoodleCrawler import settings, config, utils, mail
from pymongo import MongoClient


class HomeCrawler(scrapy.Spider):
    name = 'home'

    client = MongoClient(settings.MONGO_URI)
    client['admin'].authenticate(config.MONGO_USER, config.MONGO_PASSWORD)
    user_db = client[settings.MONGO_DATABASE]['users']
    users = user_db.find()

    crawled = set()

    def start_requests(self):
        for i, user in enumerate(self.users):
            recipient = user['email']
            print(user['email'])
            request = FormRequest(url='http://218.94.159.99/login/index.php',
                                  formdata={
                                      'username': user['email'],
                                      'password': utils.decrypt(user['password']),
                                      'rememberusername': '1'
                                  },
                                  dont_filter=True,
                                  meta={'cookiejar': i},
                                  callback=self.after_login)
            request.meta['recipient'] = recipient
            yield request

    def after_login(self, response):
        """get every course id and get the first branch of it, which will be 课件,作业,etc"""
        # TODO: after a semester end, stop crawl it anymore
        sesskey = re.search('"sesskey":"([^,]*)"', response.text).group(1)
        element_ids = response.css('.type_course.depth_3.contains_branch p::attr(id)').extract()[:10]
        # element_id = element_ids[0]
        for element_id in element_ids:
            course_id = element_id.split('_')[-1]
            if course_id in self.crawled:
                # if changed, send_email
                print('crawled')
                print(mail.changed_courses)
                mail.send_mail("MoodleUpdate", response.meta['recipient'], course_id)
                # continue
            else:
                request = FormRequest(url='http://218.94.159.99/lib/ajax/getnavbranch.php',
                                      formdata={
                                          'elementid': element_id,
                                          'id': course_id,
                                          'type': element_id.split('_')[-2],
                                          'sesskey': sesskey,
                                          'instance': '4'
                                      },
                                      meta={'cookiejar': response.meta['cookiejar']},
                                      callback=self.get_branch)
                print(response.meta['recipient'], ': first branch')
                request.meta['sesskey'] = sesskey
                request.meta['recipient'] = response.meta['recipient']
                yield request
        # for course_name in courses:
        #     print(course_name)
        # links = response.css('.course_title h2.title a::attr(href)').extract()
        # for link in links:
        #     yield Request(url=link)

    def get_branch(self, response):
        """read the first branch of it, which will be 课件,作业,etc. And request meta data, 具体作业，具体课件"""
        course_dict = json.loads(response.text)
        course = Course()
        course['name'] = course_dict['name']
        course['key'] = course_dict['key']
        course['children'] = []
        course['email'] = response.meta['recipient']
        for child in course_dict['children']:
            if child['requiresajaxloading']:
                element_id = child['id']

                request = FormRequest(url='http://218.94.159.99/lib/ajax/getnavbranch.php',
                                      formdata={
                                          'elementid': element_id,
                                          'id': element_id.split('_')[-1],
                                          'type': element_id.split('_')[-2],
                                          'sesskey': response.meta['sesskey'],
                                          'instance': '4'
                                      },
                                      meta={'cookiejar': response.meta['cookiejar']},
                                      callback=self.get_meta,
                                      )
                print(response.meta['recipient'], ': second branch')

                request.meta['course'] = course
                request.meta['lenth'] = len(course_dict['children'])
                yield request

    def get_meta(self, response):
        course = response.meta['course']
        branch_dict = json.loads(response.text)
        course_sub1 = Course()
        course_sub1['name'] = branch_dict['name']
        course_sub1['key'] = branch_dict['key']
        course_sub1['children'] = []
        if 'children' in branch_dict.keys():
            # TODO add diretory scrapying and
            for item_sub2 in branch_dict['children']:
                course_sub2 = CourseItem()
                if isinstance(item_sub2, str):
                    course_sub2['name'] = item_sub2
                else:
                    course_sub2['name'] = item_sub2['name']
                    course_sub2['key'] = item_sub2['key']
                    course_sub2['link'] = item_sub2['link']
                course_sub1['children'].append(dict(course_sub2))
        course['children'].append(dict(course_sub1))
        if response.meta['lenth'] - 2 == len(course['children']):  # sub the two not ajax
            # pprint.pprint(course)
            print(course['name'], '爬取完成')
            self.crawled.add(course['key'])

            yield course

    def parse(self, response):
        pass
        # course_name = response.css('.page-header-headings h1::text').extract_first()
        # print(course_name)
        # open_in_browser(response)

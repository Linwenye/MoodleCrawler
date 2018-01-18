import scrapy
from scrapy.utils.response import open_in_browser
from scrapy.http import Request, FormRequest
from MoodleCrawler import config
import re
import pprint
import json
from MoodleCrawler.items import Course
from MoodleCrawler.items import CourseItem
from scrapy.loader import ItemLoader


class HomeCrawler(scrapy.Spider):
    name = 'home'

    start_urls = ['http://218.94.159.99/my/']

    def start_requests(self):
        return [FormRequest(url='http://218.94.159.99/login/index.php',
                            formdata={
                                'username': config.username,
                                'password': config.password,
                                'rememberusername': '1'
                            },
                            callback=self.after_login,
                            )]

    def after_login(self, response):
        self.sesskey = re.search('"sesskey":"([^,]*)"', response.text).group(1)
        element_ids = response.css('.type_course.depth_3.contains_branch p::attr(id)').extract()
        # for element_id in element_ids: # TODO: it's just for debugging to only just use one item
        element_id = element_ids[0]
        yield FormRequest(url='http://218.94.159.99/lib/ajax/getnavbranch.php',
                          formdata={
                              'elementid': element_id,
                              'id': element_id.split('_')[-1],
                              'type': element_id.split('_')[-2],
                              'sesskey': self.sesskey,
                              'instance': '4'
                          },
                          callback=self.get_branch,
                          )
        # for course_name in courses:
        #     print(course_name)
        # links = response.css('.course_title h2.title a::attr(href)').extract()
        # for link in links:
        #     yield Request(url=link)

    def get_branch(self, response):
        course_dict = json.loads(response.text)
        course = Course()
        course['name'] = course_dict['name']
        course['key'] = course_dict['key']
        course['children'] = []

        for child in course_dict['children']:
            if child['requiresajaxloading']:
                element_id = child['id']

                request = FormRequest(url='http://218.94.159.99/lib/ajax/getnavbranch.php',
                                      formdata={
                                          'elementid': element_id,
                                          'id': element_id.split('_')[-1],
                                          'type': element_id.split('_')[-2],
                                          'sesskey': self.sesskey,
                                          'instance': '4'
                                      },
                                      callback=self.get_meta,
                                      )
                print(course_dict['name'])
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
        for item_sub2 in branch_dict['children']:
            course_sub2 = CourseItem()
            course_sub2['name'] = item_sub2['name']
            course_sub2['key'] = item_sub2['key']
            course_sub1['children'].append(dict(course_sub2))

        course['children'].append(dict(course_sub1))
        if response.meta['lenth'] - 2 == len(course['children']):  # sub the two not ajax
            pprint.pprint(course)
            return course

    def parse(self, response):
        pass
        # course_name = response.css('.page-header-headings h1::text').extract_first()
        # print(course_name)
        # open_in_browser(response)

# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Course(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    key = scrapy.Field()
    children = scrapy.Field()


class CourseItem(scrapy.Item):
    name = scrapy.Field()
    key = scrapy.Field()

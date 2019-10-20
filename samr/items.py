# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SamrItem(scrapy.Item):
    tag = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()
    releaseTime = scrapy.Field()
    keyWorlds = scrapy.Field()

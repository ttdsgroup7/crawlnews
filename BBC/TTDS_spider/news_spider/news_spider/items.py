# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    headline = scrapy.Field()
    publish_time = scrapy.Field()
    content = scrapy.Field()
    url = scrapy.Field()
    image = scrapy.Field()
    location = scrapy.Field()
    related_topic = scrapy.Field()

    pass

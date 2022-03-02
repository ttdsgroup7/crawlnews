import logging
import re

import scrapy
from scrapy import Request
import json
from scrapy.settings.default_settings import DEFAULT_REQUEST_HEADERS
from news_spider.items import NewsSpiderItem

logger2 = logging.getLogger()
level = logging.INFO
logger2.setLevel(level)

hdlr2 = logging.FileHandler("./spider2.log", encoding='utf-8')
hdlr2.setLevel(level)
logger2.addHandler(hdlr2)


class BbcNewsSpider(scrapy.Spider):
    name = 'BBC_news'
    allowed_domains = ['bbc.co.uk']
    start_urls = []
    location_list = ['United Kingdom', 'United Kingdom', 'United Kingdom', 'United Kingdom', 'Europe', 'Europe',
                     'Europe',
                     'Africa', 'China', 'India', 'Australia', 'US&Canada', '', '', '', '', '', '', '', 'Latin America',
                     'Middle East']

    topic_list = ['world', 'world', 'world', 'world', 'world', 'world', 'world', 'world', 'world', 'world', 'world',
                  'world', 'business',
                  'politics', 'tech', 'science', 'health', 'education', 'entertainment', 'world', 'world']

    def start_requests(self):
        DEFAULT_REQUEST_HEADERS['Accept'] = '*/*'
        DEFAULT_REQUEST_HEADERS['Host'] = 'bbc.co.uk'
        DEFAULT_REQUEST_HEADERS['Referer'] = 'https://bbc.co.uk/'

        with open("./news_spider/spiders/website.txt", mode='r', encoding='utf8') as f:
            for url in f.readlines():
                self.start_urls.append(url)
        # self.start_urls = self.start_urls[14:]
        for index in range(len(self.start_urls)):
            req = Request(self.start_urls[index].format(category="news"), callback=self.parse_json,
                          meta={"location": self.location_list[index], 'topic': self.topic_list[index],
                                "url": self.start_urls[index]},
                          encoding='utf-8')
            yield req

            for pageNum in range(2, 51):
                try:
                    pre_post = re.match(r'(.*pageNumber%2F)\d+(%.*)', self.start_urls[index])
                    url = pre_post.group(1) + str(pageNum) + pre_post.group(2)
                    req = Request(url.format(category="news"), callback=self.parse_json,
                                  meta={"location": self.location_list[index], 'topic': self.topic_list[index],
                                        "url": self.start_urls[index]},
                                  encoding='utf-8')
                    yield req
                except BaseException as e:
                    print("pageNum error:", e)

    def parse_json(self, response):
        json_str = json.loads(response.text)
        news_list = json_str['payload'][0]['body']['results']
        metadata = {}
        for news in news_list:
            try:
                if 'url' in news:
                    metadata['url'] = 'https://bbc.co.uk' + news['url']
                    metadata['lastUpdated'] = news['lastUpdated']
                    metadata['image'] = news['image']['href']
                    metadata['headline'] = news['summary']
                    metadata['location'] = response.meta.get('location')
                    metadata['topic'] = response.meta.get('topic')
                    yield Request(metadata["url"], callback=self.parse_content, meta=metadata)
            except BaseException as e:
                print("something is wrong here:", e)

    def parse_content(self, response):
        tag = re.search(r'https://bbc.co.uk/(.*)', response.meta.get("url", ""), re.I).group(1)
        text = response.xpath("//article/div//p//text()").getall()
        content = ''
        # combine sentences
        for i in range(len(text)):
            if i == 0:
                pass
            else:
                content += text[i] + ' '
        # related_topic = str(response.xpath("//article/section//li/a/text()").getall())[1:-1]
        news_item = NewsSpiderItem()
        _datetime = response.meta.get('lastUpdated')[:-6].replace('T', ' ')
        news_item['headline'] = response.meta.get('headline')
        news_item['publish_time'] = _datetime
        news_item['content'] = content
        news_item['url'] = response.meta.get('url')
        news_item['image'] = response.meta.get('image')
        news_item['location'] = response.meta.get('location')
        news_item['related_topic'] = response.meta.get('topic')
        if content and news_item['headline']:
            # logger2.info(news_item['headline'] + '--' + news_item['related_topic'] + "was submitted")
            yield news_item

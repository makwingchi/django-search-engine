# -*- coding: utf-8 -*-
import scrapy
import json

from scrapy.loader import ItemLoader

from ArticleSpider.items import TechcrunchItem


class TechcrunchSpider(scrapy.Spider):
    name = 'techcrunch'
    allowed_domains = ['techcrunch.com']
    start_urls = ['https://techcrunch.com/wp-json/tc/v1/magazine?page={}&_embed=true&cachePrevention=0']

    def parse(self, response):
        # Parse tech news from the last 3 years
        for i in range(1, 1800):
            yield scrapy.Request(url=self.start_urls[0].format(i), callback=self.parse_json)

    def parse_json(self, response):
        length = len(json.loads(response.body_as_unicode()))
        for i in range(length):
            url = json.loads(response.body_as_unicode())[i]["link"]
            yield scrapy.Request(url=url, callback=self.parse_news)

    def parse_news(self, response):
        item_loader = ItemLoader(item=TechcrunchItem(), response=response)

        item_loader.add_css("title", ".article__title::text")
        item_loader.add_css("content", ".article-content p::text")
        item_loader.add_css("publish_time", "meta[name='sailthru.date']::attr(content)")
        item_loader.add_value("url", response.url)

        yield item_loader.load_item()
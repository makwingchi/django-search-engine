# -*- coding: utf-8 -*-

from urllib import parse

import scrapy
from scrapy.loader import ItemLoader
from scrapy_redis.spiders import RedisSpider


from ArticleSpider.items import AmazonItem


class AmazonSpider(RedisSpider):
    name = 'amazon'
    allowed_domains = ['amazon.com']
    redis_key = "amazon:start_urls"
    # terms = ["laptop", "desktop", "computer", "lenovo", "apple", "dell",
    #          "samsung", "sony", "huawei", "phone", "camera", "tv", "mobile+phone",
    #          "router", "projector", "headset", "computer+mouse", "keyboard",
    #          "speaker", "clock", "remote", "alexa", "cable", "earbud", "kindle",
    #          "wifi", "ring", "tablet", "wireless", "monitors", "adapter",
    #          "repeater", "adapter", "modem", "access+point", "hard+drive",
    #          "memory+card", "webcam", "processor"]
    # start_urls = ['https://www.amazon.com/{0}/s?k={0}&page=1'.format(term) for term in terms]

    # start_urls = ['https://www.amazon.com']

    def parse(self, response):

        # For parsing Amazon home page
        # all_urls = response.css(".a-list-item .a-link-normal.a-inline-block::attr(href)").extract()
        # all_urls = [parse.urljoin(response.url, url) for url in all_urls]

        # For parsing specific search terms
        all_urls = response.css(".a-section.a-spacing-none .rush-component .a-link-normal::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]

        # For all parsing jobs
        all_urls = filter(lambda x: True if x.startswith("https") else False, all_urls)

        for url in all_urls:
            yield scrapy.Request(url=url, callback=self.parse_product)

        # For parsing specific search terms
        # Next page
        next_url = response.css(".a-last a::attr(href)").extract_first("")
        yield scrapy.Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_product(self, response):
        all_urls = response.css('.a-carousel-card .a-link-normal[rel="noopener"]::attr(href)').extract()

        item_loader = ItemLoader(item=AmazonItem(), response=response)
        item_loader.add_css("title", "#productTitle::text")
        item_loader.add_xpath(
            "price", "//*[@id = 'priceblock_ourprice' or @id = 'priceblock_dealprice' or @id = 'priceblock_saleprice']/text()"
        )
        item_loader.add_css("ratings", "#acrCustomerReviewText::text")
        item_loader.add_css("stars", ".a-icon.a-icon-star .a-icon-alt::text")
        item_loader.add_css("category", "#wayfinding-breadcrumbs_feature_div li:nth-child(1) span a::text")
        item_loader.add_css("features", "#feature-bullets ul.a-unordered-list.a-vertical.a-spacing-none span.a-list-item::text")
        item_loader.add_value("url", response.url)

        product_item = item_loader.load_item()
        yield product_item

        for url in all_urls:
            yield scrapy.Request(url=url, callback=self.parse_product)
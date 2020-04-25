# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import datetime
import re

import scrapy
from ArticleSpider.models.es_types import CommonType
from ArticleSpider.settings import SQL_DATETIME_FORMAT
from ArticleSpider.utils.common import get_md5
from elasticsearch_dsl.connections import connections
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst

es = connections.create_connection(CommonType._get_using)


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def date_convert(value):
    match_re = re.match(".*?(\d+.*)", value)
    if match_re:
        return match_re.group(1)
    else:
        return "1970-07-01"


def gen_suggests(index, info_tuple, analyzer="standard"):
    # generate suggests based on input string
    used_words = set()
    suggestions = []
    for text, weight in info_tuple:
        if text:
            # analyze input string
            words = es.indices.analyze(index=index, analyzer=analyzer, params={'filter': ["lowercase"]}, body=text)
            analyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"]) > 1])
            new_words = analyzed_words - used_words
            used_words = used_words | new_words
        else:
            new_words = set()

        if new_words:
            suggestions.append({"input": list(new_words), "weight": weight})
            used_words.update(new_words)

    return suggestions


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


def remove_dollar_sign(value):
    return value.replace("$", "").replace("₹", "")


def take_first_value(value):
    return value.split(' ')[0]


def handle_spaces(value):
    lst = value.split("\n")
    clean_lst = [element.strip() for element in lst]
    return "".join(clean_lst)


class AmazonItem(scrapy.Item):
    url = scrapy.Field(
        output_processor=TakeFirst()
    )
    url_object_id = scrapy.Field(
        output_processor=TakeFirst()
    )
    title = scrapy.Field(
        output_processor=TakeFirst()
    )
    price = scrapy.Field(
        output_processor=TakeFirst()
    )
    ratings = scrapy.Field(
        output_processor=TakeFirst()
    )
    stars = scrapy.Field(
        output_processor=TakeFirst()
    )
    features = scrapy.Field()
    category = scrapy.Field(
        output_processor=TakeFirst()
    )

    def get_insert_sql(self):
        insert_sql = """
            insert into amazon(url, url_object_id, title, price, ratings, stars, features, category)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE title=VALUES(title), price=VALUES(price), ratings=VALUES(ratings),
                stars=VALUES(stars), features=VALUES(features), category=VALUES(category)
        """

        # print(handle_spaces(self.get("title", "not found")))
        # print(self.get("price", "0"))
        # print(take_first_value(self.get("ratings", " ")))
        # print(take_first_value(self.get("stars", " ")))
        # print(" ".join([feature.strip() for feature in self["features"]]))

        title = handle_spaces(self.get("title", "not found"))
        url_object_id = get_md5(title)
        price = float(remove_dollar_sign(self.get("price", "0").replace(",", "")))
        ratings = int(take_first_value(self.get("ratings", "0 ")).replace(",", ""))
        stars = float(take_first_value(self.get("stars", "0 ")))
        category = handle_spaces(self.get("category", "\n"))
        features = " ".join([feature.strip() for feature in self.get("features", [])])

        params = (
            self["url"], url_object_id, title,
            price, ratings, stars, features, category
        )

        return insert_sql, params

    def save_to_es(self):
        # from item to es
        product = CommonType()
        product.title = handle_spaces(self.get("title", "not found"))
        product.content = " ".join([feature.strip() for feature in self.get("features", [])])
        product.url = self["url"]
        product.meta.id = get_md5(product.title)
        product.source = "Amazon"

        product.suggest = gen_suggests(CommonType._doc_type.index, ((product.title, 10), (product.content, 6)))

        product.save()
        return


class TechcrunchItem(scrapy.Item):
    url = scrapy.Field(
        output_processor=TakeFirst()
    )
    url_object_id = scrapy.Field()
    title = scrapy.Field(
        output_processor=TakeFirst()
    )
    content = scrapy.Field()
    publish_time = scrapy.Field(
        output_processor=TakeFirst()
    )

    def get_insert_sql(self):
        insert_sql = """
            insert into techcrunch(url, url_object_id, title, content, publish_time)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE title=VALUES(title), content=VALUES(content), publish_time=VALUES(publish_time)
        """

        url_object_id = get_md5(self["url"])
        content = "\n".join(self["content"])
        publish_time = datetime.datetime.strptime(self["publish_time"], SQL_DATETIME_FORMAT)

        params = (
            self["url"], url_object_id, self["title"],
            content, publish_time
        )

        return insert_sql, params

    def save_to_es(self):
        # from item to es
        news = CommonType()
        news.title = self["title"]
        news.content = "\n".join(self["content"])
        news.url = self["url"]
        news.meta.id = get_md5(self["title"])
        news.source = "TechCrunch"

        news.suggest = gen_suggests(CommonType._get_index, ((news.title, 10), (news.content, 6)))

        news.save()
        return

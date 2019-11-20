# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import datetime
import re

import scrapy
from scrapy.loader.processors import TakeFirst, Identity, MapCompose, Join
from scrapy.loader import ItemLoader

from ArticleSpider.models.es_types import CommonType
from ArticleSpider.utils.common import extract_num, get_md5
from ArticleSpider.settings import SQL_DATE_FORMAT, SQL_DATETIME_FORMAT

from w3lib.html import remove_tags

from elasticsearch_dsl.connections import connections

es = connections.create_connection(CommonType._doc_type.using)

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


class ZhihuQuestionItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into zhihu_question(zhihu_id, topics, url, title, content, answer_num, comments_num,
              watch_user_num, click_num, crawl_time
              )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num), comments_num=VALUES(comments_num),
              watch_user_num=VALUES(watch_user_num), click_num=VALUES(click_num)
        """

        zhihu_id = "".join(self["zhihu_id"])
        topics = ",".join(self["topics"])
        url = "".join(self["url"])
        title = "".join(self["title"])
        content = "".join(self["content"])
        answer_num = extract_num("".join(self["answer_num"]).replace(",", "")) if "," in "".join(
            self["answer_num"]) else extract_num("".join(self["answer_num"]))
        comments_num = extract_num("".join(self["comments_num"]).replace(",", "")) if "," in "".join(
            self["comments_num"]) else extract_num("".join(self["comments_num"]))
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        if len(self["watch_user_num"]) == 2:
            watch_user_num = int(self["watch_user_num"][0].replace(",", ""))
            click_num = int(self["watch_user_num"][1].replace(",", ""))
        else:
            watch_user_num = int(self["watch_user_num"][0].replace(",", ""))
            click_num = 0

        params = (zhihu_id, topics, url, title, content, answer_num,
                  comments_num, watch_user_num, click_num, crawl_time)
        return insert_sql, params

    def save_to_es(self):
        # from item to es
        qa = CommonType()
        qa.title = "".join(self["title"])
        content = [remove_tags(content).strip() for content in self["content"]]
        qa.content = " ".join(content)
        qa.url = "".join(self["url"])
        qa.meta.id = get_md5(qa.title)
        qa.source = "Zhihu"

        qa.suggest = gen_suggests(CommonType._doc_type.index, ((qa.title, 10), (qa.content, 6)), "ik_max_word")

        qa.save()
        return
    

class ZhihuAnswerItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    question_title = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                    insert into zhihu_answer(zhihu_id, url, question_id, author_id, content, praise_num, comments_num,
                      create_time, update_time, crawl_time
                      ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                      ON DUPLICATE KEY UPDATE content=VALUES(content), comments_num=VALUES(comments_num), praise_num=VALUES(praise_num),
                      update_time=VALUES(update_time)
                """

        create_time = datetime.datetime.fromtimestamp(self["create_time"]).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self["update_time"]).strftime(SQL_DATETIME_FORMAT)
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)
        params = (
            self["zhihu_id"], self["url"], self["question_id"],
            self["author_id"], self["content"], self["praise_num"],
            self["comments_num"], create_time, update_time, crawl_time
        )

        return insert_sql, params

    def save_to_es(self):
        # from item to es
        qa = CommonType()
        qa.title = self["question_title"]
        qa.content = remove_tags(self["content"])
        qa.url = self["url"]
        qa.meta.id = get_md5(self["url"])
        qa.source = "Zhihu"

        qa.suggest = gen_suggests(CommonType._doc_type.index, ((qa.title, 10), (qa.content, 6)), "ik_max_word")

        qa.save()
        return


def remove_dollar_sign(value):
    return value.replace("$", "").replace("₹", "")


def take_first_value(value):
    return value.split(' ')[0]


def handle_spaces(value):
    lst = value.split("\n")
    clean_lst = [element.strip() for element in lst ]
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

        news.suggest = gen_suggests(CommonType._doc_type.index, ((news.title, 10), (news.content, 6)))

        news.save()
        return

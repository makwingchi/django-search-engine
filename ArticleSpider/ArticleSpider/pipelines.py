# -*- coding: utf-8 -*-
import codecs
import json

import MySQLdb
from MySQLdb.cursors import DictCursor
from scrapy.exporters import JsonItemExporter
from scrapy.pipelines.images import ImagesPipeline
from twisted.enterprise import adbapi


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item

class MysqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect("127.0.0.1", "root", "123456", "article_spider", charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into jobbole_article(title, url, url_object_id, front_image_url, front_image_path, praise_nums, comment_nums, fav_nums, tags, content, create_date)
            values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE praise_nums=VALUES(praise_nums)
        """
        params = list()
        params.append(item.get("title", ""))
        params.append(item.get("url", ""))
        params.append(item.get("url_object_id", ""))
        front_image = ",".join(item.get("front_image_url", []))
        params.append(front_image)
        params.append(item.get("front_image_path", ""))
        params.append(item.get("praise_nums", 0))
        params.append(item.get("comment_nums", 0))
        params.append(item.get("fav_nums", 0))
        params.append(item.get("tags", ""))
        params.append(item.get("content", ""))
        params.append(item.get("create_date", "1970-07-01"))
        # print(params)

        self.cursor.execute(insert_sql, tuple(params))
        self.conn.commit()

        return item

class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        print(failure)

    def do_insert(self, cursor, item):
        # insert items to database
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)


class JsonWithEncodingPipeline(object):
    # Export json files
    def __init__(self):
        self.file = codecs.open("article.json", "w", encoding="utf-8")

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()

class JsonExporterPipeline(object):
    def __init__(self):
        self.file = open("articleexport.json", "wb")
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            image_file_path = ""
            for ok, value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path

        return item

class ElasticsearchPipeline(object):
    # write data to es
    def process_item(self, item, spider):
        item.save_to_es()
        return item
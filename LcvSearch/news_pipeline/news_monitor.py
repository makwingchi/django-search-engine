# -*- coding: utf-8 -*-

import os
import sys
import redis
import hashlib
import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "common"))

import news_api_client
from cloudAMQP_client import CloudAMQPClient

REDIS_HOST = "localhost"
REDIS_PORT = 6379

NEWS_TIME_OUT_IN_SECONDS = 3600 * 24
SLEEP_TIME_IN_SECONDS = 5 * 60

SCRAPE_NEWS_TASK_QUEUE_URL = "amqp://ywcixiii:AQtEfYcJquJVjkZexYqTiJ95bP_898JP@crane.rmq.cloudamqp.com/ywcixiii"
SCRAPE_NEWS_TASK_QUEUE_NAME = "scrape-news-task-queue"

NEWS_SOURCES = [
    'cnn',
    'bbc-news',
    'bloomberg',
    'espn',
    'nbc-news',
    'techcrunch',
    'the-wall-street-journal',
    'the-new-york-times',
    'abc-news',
    'fox-sports',
    'the-washington-post'
]

redis_client = redis.StrictRedis(REDIS_HOST, REDIS_PORT)
cloudAMQP_client = CloudAMQPClient(SCRAPE_NEWS_TASK_QUEUE_URL, SCRAPE_NEWS_TASK_QUEUE_NAME)

while True:
    news_list = news_api_client.get_news_from_source(NEWS_SOURCES)

    num_of_new_news = 0

    for news in news_list:
        news_digest = hashlib.md5(news["title"].encode("utf-8")).digest().hex()

        if redis_client.get(news_digest) is None:
            num_of_new_news += 1
            news["digest"] = news_digest

            if news["publishedAt"] is None:
                # 2020-05-03T16:22:35.2508281Z
                news["publishedAt"] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

            redis_client.set(news_digest, 1)
            redis_client.expire(news_digest, NEWS_TIME_OUT_IN_SECONDS)

            cloudAMQP_client.send_message(news)

    print("Fetched %d new news." % num_of_new_news)

    cloudAMQP_client.sleep(SLEEP_TIME_IN_SECONDS)

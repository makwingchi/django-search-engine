# -*- coding: utf-8 -*-

import os
import sys
from newspaper import Article

# import common package in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))

from cloudAMQP_client import CloudAMQPClient

# Use Cloud AMQP queue
DEDUPE_NEWS_TASK_QUEUE_URL = "amqp://arzcmkvz:opl4ObOpTJiiv7sNr-96akzjm_zSbBjA@jellyfish.rmq.cloudamqp.com/arzcmkvz"
DEDUPE_NEWS_TASK_QUEUE_NAME = "dedupe-news-task-queue"
SCRAPE_NEWS_TASK_QUEUE_URL = "amqp://ywcixiii:AQtEfYcJquJVjkZexYqTiJ95bP_898JP@crane.rmq.cloudamqp.com/ywcixiii"
SCRAPE_NEWS_TASK_QUEUE_NAME = "scrape-news-task-queue"

SLEEP_TIME_IN_SECONDS = 5

dedupe_news_queue_client = CloudAMQPClient(DEDUPE_NEWS_TASK_QUEUE_URL, DEDUPE_NEWS_TASK_QUEUE_NAME)
scrape_news_queue_client = CloudAMQPClient(SCRAPE_NEWS_TASK_QUEUE_URL, SCRAPE_NEWS_TASK_QUEUE_NAME)


def _handle_message(message):
    if message is None or not isinstance(message, dict):
        print("message is broken")
        return

    task = message

    article = Article(task['url'])
    article.download()
    article.parse()

    task['content'] = article.text

    dedupe_news_queue_client.send_message(task)


while True:
    # fetch msg from queue
    if scrape_news_queue_client is not None:
        msg = scrape_news_queue_client.get_message()
        if msg is not None:
            try:
                _handle_message(msg)
            except Exception as e:
                pass
        scrape_news_queue_client.sleep(SLEEP_TIME_IN_SECONDS)
# -*- coding: utf-8 -*-

import datetime
import os
import sys

from dateutil import parser
from elasticsearch import Elasticsearch
from sklearn.feature_extraction.text import TfidfVectorizer

# import common and search packages in parent directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'common'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'search'))

from cloudAMQP_client import CloudAMQPClient
from models import CommonType


# Use Cloud AMQP queue
DEDUPE_NEWS_TASK_QUEUE_URL = "amqp://arzcmkvz:opl4ObOpTJiiv7sNr-96akzjm_zSbBjA@jellyfish.rmq.cloudamqp.com/arzcmkvz"
DEDUPE_NEWS_TASK_QUEUE_NAME = "dedupe-news-task-queue"

SLEEP_TIME_IN_SECONDS = 1

NEWS_TABLE_NAME = "news"

SAME_NEWS_SIMILARITY_THRESHOLD = 0.9

cloudAMQP_client = CloudAMQPClient(DEDUPE_NEWS_TASK_QUEUE_URL, DEDUPE_NEWS_TASK_QUEUE_NAME)
es_client = Elasticsearch(hosts=["127.0.0.1"])


def _handle_message(message):
    if message is None or not isinstance(message, dict):
        return
    task = message
    text = str(task['content'])
    if text is None:
        return

    # get all recent news based on publishedAt
    published_at = parser.parse(task['publishedAt'])
    published_at_day_begin = datetime.datetime(published_at.year, published_at.month, published_at.day, 0, 0, 0, 0)
    published_at_day_end = published_at_day_begin + datetime.timedelta(days=1)

    # search from elasticsearch based on publishedAt
    response = es_client.search(
        index=NEWS_TABLE_NAME,
        body={
            "query": {
                "range": {
                    "publishedAt": {
                        "gte": published_at_day_begin,
                        "lte": published_at_day_end
                    }
                }
            }
        }
    )

    same_day_news_list = [hit for hit in response['hits']['hits']]

    if same_day_news_list is not None and len(same_day_news_list) > 0:
        documents = [str(news["_source"]['content']) for news in same_day_news_list]
        documents.insert(0, text)

        # Calculate similarity matrix
        tfidf = TfidfVectorizer().fit_transform(documents)
        pairwise_sim = tfidf * tfidf.T

        print(pairwise_sim.A)

        rows, _ = pairwise_sim.shape

        # Check if news are duplicated
        for row in range(1, rows):
            if pairwise_sim[row, 0] > SAME_NEWS_SIMILARITY_THRESHOLD:
                # Duplicated news. Ignore.
                print("Duplicated news. Ignore.")
                return

    task['publishedAt'] = parser.parse(task['publishedAt'])

    # save non-duplicated news to database
    news = CommonType()
    news.title = task["title"]
    news.content = task["content"]
    news.url = task["url"]
    news.source = task["source"]
    news.author = task["author"]
    news.description = task["description"]
    news.urlToImage = task["urlToImage"]
    news.publishedAt = task["publishedAt"]

    news.save()


while True:
    if cloudAMQP_client is not None:
        msg = cloudAMQP_client.get_message()
        if msg is not None:
            # Parse and process the task
            try:
                _handle_message(msg)
            except Exception as e:
                print(e)
                pass

        cloudAMQP_client.sleep(SLEEP_TIME_IN_SECONDS)

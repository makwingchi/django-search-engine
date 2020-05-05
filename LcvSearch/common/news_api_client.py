import requests
from json import loads

NEWS_API_ENDPOINT = "https://newsapi.org/v2/"
NEWS_API_KEY = "0badd6f073d54cd1a6438f3626f009e5"
ARTICLES_API = "top-headlines"

CNN = "cnn"
DEFAULT_SOURCES = [CNN]
SORT_BY_TOP = "top"


def _build_url(end_point=NEWS_API_ENDPOINT, api_name=ARTICLES_API):
    return end_point + api_name


def get_news_from_source(sources=DEFAULT_SOURCES, sort_by=SORT_BY_TOP):
    articles = []
    for source in sources:
        payload = {"apiKey": NEWS_API_KEY,
                   "sources": source,
                   "sortBy": sort_by}
        response = requests.get(_build_url(), params=payload)
        res_json = loads(response.content)

        # Extract info from response
        if res_json and res_json["status"] == "ok":
            for news in res_json["articles"]:
                news["source"] = source
            articles.extend(res_json["articles"])

    return articles

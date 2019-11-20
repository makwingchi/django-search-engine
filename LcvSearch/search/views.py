from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import View
import json
import redis

from search.models import CommonType
from elasticsearch import Elasticsearch

client = Elasticsearch(hosts=["127.0.0.1"])
redis_cli = redis.StrictRedis(host='localhost', port=6379, db=0, password="123456")


class IndexView(View):
    # Home page
    def get(self, request):
        topn_search = redis_cli.zrevrangebyscore("search_keyword_set", "+inf", "-inf", start=0, num=5)
        topn_search = [search.decode("utf-8") for search in topn_search]
        return render(request, "index.html", {"topn_search": topn_search})

class SearchSuggest(View):
    def get(self, request):
        keywords = request.GET.get("s", "")
        re_datas = []
        if keywords:
            s = CommonType.search()
            s = s.suggest("my_suggest", keywords, completion={
                "field": "suggest",
                "fuzzy": {
                    "fuzziness": 2,
                },
                "size": 10
            })
            suggestions = s.execute_suggest()
            for match in suggestions.my_suggest[0].options:
                source = match._source
                re_datas.append(source["title"])

        return HttpResponse(json.dumps(re_datas), content_type="application/json")

class SearchView(View):
    def get(self, request):
        keywords = request.GET.get("q", "")
        # s_type = request.GET.get("s_type", "article")

        redis_cli.zincrby("search_keyword_set", 1, keywords)
        topn_search = redis_cli.zrevrangebyscore("search_keyword_set", "+inf", "-inf", start=0, num=5)
        topn_search = [search.decode("utf-8") for search in topn_search]
        page = request.GET.get("p", "1")
        try:
            page = int(page)
        except:
            page = 1

        start_time = datetime.now()
        response = client.search(
            index = "data",
            body = {
                "query": {
                    "multi_match": {
                        "query": keywords,
                        "fields": ["title", "content"]
                    }
                },
                # pagination
                "from": (page-1)*10,
                "size": 10,
                # highlight keywords
                "highlight": {
                    "pre_tags": ["<span class='keyWord'>"],
                    "post_tags": ["</span>"],
                    "fields": {
                        "title": {},
                        "content": {}
                    }
                }
            }
        )
        end_time = datetime.now()
        last_seconds = (end_time - start_time).total_seconds()

        total_nums = response["hits"]["total"]
        if (page % 10) > 0:
            page_nums = int(total_nums/10 + 1)
        else:
            page_nums = int(total_nums/10)

        hit_list = []
        for hit in response["hits"]["hits"]:
            hit_dict = {}
            if "title" in hit["highlight"]:
                hit_dict["title"] = "".join(hit["highlight"]["title"])
            else:
                hit_dict["title"] = hit["_source"]["title"]
            if "content" in hit["highlight"]:
                hit_dict["content"] = "".join(hit["highlight"]["content"])[:500]
            else:
                hit_dict["content"] = hit["_source"]["content"][:500]

            hit_dict["source"] = hit["_source"]["source"]
            hit_dict["url"] = hit["_source"]["url"]
            hit_dict["score"] = round(hit["_score"], 2)

            hit_list.append(hit_dict)

        amazon, techcrunch, zhihu = 0, 0, 0
        for hit in hit_list:
            if hit["source"] == "Amazon":
                amazon += 1
            if hit["source"] == "TechCrunch":
                techcrunch += 1
            if hit["source"] == "Zhihu":
                zhihu += 1

        return render(request, "result.html", {"all_hits": hit_list,
                                               "key_words": keywords,
                                               "page": page,
                                               "total_nums": total_nums,
                                               "page_nums": page_nums,
                                               "last_seconds": last_seconds,
                                               "topn_search": topn_search,
                                               "amazon": amazon,
                                               "techcrunch": techcrunch,
                                               "zhihu": zhihu})
from elasticsearch_dsl import DocType, Keyword, Text, Date
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=["localhost"])


class CommonType(DocType):
    source = Keyword()
    author = Keyword()
    title = Text()
    description = Text()
    content = Text()
    url = Keyword()
    urlToImage = Keyword()
    publishedAt = Date()

    class Index:
        name = "news"


if __name__ == "__main__":
    CommonType.init()

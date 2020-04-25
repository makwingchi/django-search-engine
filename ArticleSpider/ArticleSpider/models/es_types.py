from elasticsearch_dsl import DocType, Completion, Keyword, Text
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=["localhost"])


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])


class CommonType(DocType):
    # Common doc type for Amazon and TechCrunch
    suggest = Completion(analyzer=ik_analyzer)
    title = Text()
    url = Keyword()
    content = Text()
    source = Keyword()

    class Meta:
        index = "data"
        doc_type = "doc"


if __name__ == "__main__":
    CommonType.init()
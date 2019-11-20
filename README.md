# Library Search Engine

## Description
This is a web search engine project built mainly with Elasticsearch and the Django Framework. The data used was crawled from [Amazon](https://www.amazon.com), [TechCrunch](https://www.techcrunch.com), and [Zhihu](https://www.zhihu.com) (more than 100,000 rows in total), and stored in Elasticsearch database. 

## Features
- The search engine offers search suggestions before you've even finished typing;
- Users are able to know popular search and their more recent search terms;
- Users will be aware of the total number of results they get, the total number of pages, the amount of time the system takes to fetch those results, and the source each one of them come from;
- Pagination divides the search results into discrete pages, allowing users to view 10 results in a single page.

## Stack
- `Python`
- `Scrapy`
- `Django`
- `Elasticsearch`
- `Kibana`
- `Redis`
- `Javascript`
- `HTML/CSS`

## Demo
Search Suggestions
![demo](/Demo/suggest.PNG)


Most frequent and most recent search terms
![demo](/Demo/popular_and_recent_searches.PNG)


Result page
![demo](/Demo/search_results.PNG)


Pagination
![demo](/Demo/pagination.PNG)

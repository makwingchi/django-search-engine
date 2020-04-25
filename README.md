# Django-based Search Engine


## Overview
This is a web search engine project implemented with the Django MTV (Model-Template-View) Backend and Django Template Engine. The data used for the project
was crawled from [Amazon](https://www.amazon.com) and [TechCrunch](https://www.techcrunch.com) (more than 100,000 rows in total) using Redis-based Scrapy, 
and stored in an Elasticsearch database. 


## Tech Stack
- `Django`
- `Elasticsearch`
- `Scrapy`
- `Redis`
- `Kibana`
- `Javascript`
- `HTML/CSS`


## Features
- The search engine offers search suggestions before you've finished typing in a complete search term;
- Users are able to know popular search and their more recent search terms;
- Users will be aware of the total number of results they get, the total number of pages, the amount of time the system takes to fetch those results, and the source each one of them comes from;
- Pagination divides the search results into discrete pages, allowing users to view certain number of results in a single page.


## Preview
Search Suggestions
![demo](/Demo/suggest.PNG)


Most frequent and most recent search terms
![demo](/Demo/popular_and_recent_searches.PNG)


Result page
![demo](/Demo/search_results.PNG)


Pagination
![demo](/Demo/pagination.PNG)

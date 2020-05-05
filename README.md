# Django-based Search Engine


## Overview
This is a web search engine project implemented with the Django MTV (Model-Template-View) Backend and Django Template Engine. The data used for the project
is dynamically scraped from CNN, BBC, Bloomberg, ESPN, and some other mainstream media using the data pipeline built with Python, RabbitMQ & Redis, 
and stored in an Elasticsearch database. 


## Local Installation
Please make sure you have `Python 3`, `Django`, `Elasticsearch`, `Redis`, and `Git` installed in your local machine.

<b>Clone the repository to your local machine</b><br>
```git clone https://github.com/makwingchi/django-search-engine```<br>

<b>Run Redis via command line</b> <br>
```>redis-cli``` <br>

<b>Start a Elasticsearch server</b><br>
```>cd elasticsearch-x.y.z\bin``` <br>
```>elasticsearch.bat``` <br>

<b>Run the data pipeline to fetch news data</b><br>
```>cd LcvSearch/news_pipeline```<br>
```>python news_monitor.py```<br>
```>python news_fetcher.py```<br>
```>python news_deduper.py```<br>

<b>Start the Django Server</b><br>
```>cd LcvSearch```<br>
```>python manage.py runserver```<br>


## Tech Stack
- `Django`
- `Django Template`
- `Elasticsearch`
- `RabbitMQ`
- `Redis`
- `scikit-learn`
- `Javascript`
- `HTML/CSS`


## Preview
Search Suggestions
![demo](/Demo/suggest.PNG)


Most frequent and most recent search terms
![demo](/Demo/popular_and_recent_searches.PNG)


Result page
![demo](/Demo/search_results.PNG)


Pagination
![demo](/Demo/pagination.PNG)

## TODO
- [ ] Implement distributed scrapers to improve crawling speed
- [ ] Apply a more deliberate NLP approach to identify similar news
- [ ] Use the search engine as a platform for advertising (add user login, user click log processor, and recommender system features)
- [ ] ...
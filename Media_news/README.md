# COVID-19_RMDS

This module can scrape media articles about Coronavirus disease 2019 (COVID-19) vis a scraper or APIs.

I didn't find good free google news API, so currently I use a scraper to do this. As expected, the scraper is slower
and may crash at certain scenarios.

The module returns a list of dictionaries, including items:
source
title
content
url link
publish time
city

Update:
Found a free google news search api. It has limitation of daily queries and returned articles, but it is usable.
Please request your token for test

Main entry point is media_article.call_api(kw, apis, locations)

kw:
String with space separated words. Ex. 'covid-19' or 'covid-19 stock'

locations:
List or string. Ex. ['beijing', 'wuHan', 'US', 'Iran', 'south korea'] or 'beijing, wuHan, japan,Italy'

apis:
tuple of api function name and prefix of to be saved file
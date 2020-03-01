import requests
import time
import pandas as pd
from scraper.newsapi import gnewsapi_summaries, twitterapi_summaries
from scraper.google_news_scrape import scrape_news_summaries


def get_query(q):
    if type(q) == type([]):
        query = ' '.join(q)
    elif type(q) == type('string'):
        query = q
    else:
        query = 'error'
    return query


def get_location(locations):
    if type(locations) == type([]):
        pass
    elif type(locations) == type('string'):
        locations = locations.split(',')
    else:
        locations = 'error'
    return locations


def save_results(df, prefix):
    df.to_csv(prefix + '_article.csv', index=False)


# use newsapi
def call_api(kw, apis, locations=['']):
    query = get_query(kw)
    for api in apis:
        try:
            articles = []
            location_list = get_location(locations)
            location_col = []
            for location in location_list:
                results, n = api[0](query, location)
                articles += results
                location_col += [location.strip().lower().capitalize()] * n

            df = pd.DataFrame(data=articles)
            df['Location'] = location_col

            # can be replaced with other processing: save to DB...
            save_results(df, api[1])
        except:
            pass


kw = 'covid-19 stock'
# apis = [(scrape_news_summaries, 'scraper'), (gnewsapi_summaries, 'gnews'), (twitterapi_summaries, 'twitter')]
apis = [(gnewsapi_summaries, 'gnews'), (twitterapi_summaries, 'twitter')]
locations = ['beijing', 'wuHan', 'US', 'Iran', 'south korea', 'japan']
# locations = 'beijing, wuHan, japan,Italy'

call_api(kw, apis, locations)

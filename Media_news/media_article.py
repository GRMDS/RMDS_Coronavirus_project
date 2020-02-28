import requests
import pandas as pd
from scraper.newsapi import gnewsapi_summaries, twitterapi_summaries
from scraper.google_news_scrape import scrape_news_summaries


def get_query(q, city):
    if type(q) == type([]):
        query = ' '.join(q + [city])
    elif type(q) == type('string'):
        query = q + ' ' + city
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
    for api in apis:
        try:
            articles = []
            location_list = get_location(locations)
            location_col = []
            for location in location_list:
                query = get_query(kw, location)
                articles += api[0](query)
                location_col += [location.strip().lower().capitalize()] * len(api[0](query))

            df = pd.DataFrame(data=articles)
            df['Location'] = location_col

            # can be replaced with other processing: save to DB...
            save_results(df, api[1])
        except:
            pass


kw = 'covid-19 stock'
apis = [(scrape_news_summaries, 'scraper'), (gnewsapi_summaries, 'gnews'), (twitterapi_summaries, 'tritter')]
# apis = [(gnewsapi_summaries, 'gnews'), (twitterapi_summaries, 'twitter')]
locations = ['beijing', 'wuHan', 'US', 'Iran', 'south korea']
# locations = 'beijing, wuHan, japan,Italy'

call_api(kw, apis, locations)

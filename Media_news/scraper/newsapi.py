import requests
from TwitterSearch import *

def newsapi_summaries(q, start=None, sort=None):
    apikey = 'apiKey=4252de891ec04dd5bdb5554b8b7a9ad5'
    query = 'q=' + q + '&'
    url = 'http://newsapi.org/v2/top-headlines?' + query
    if start is not None:
        start = 'from=' + start + '&'
        url += start
    if sort is not None:
        sort = 'sortBy=' + sort + '&'
        url += sort
    url += apikey

    r = requests.get(url)
    articles = r.json()['articles']
    return articles


def gnewsapi_summaries(query, location):
    API_Token = '02bc6d7c6aca458da20650457dd6c934'
    query = query + ' ' + location
    url = 'https://gnews.io/api/v3/search?q={}&token={}'.format(query,API_Token)
    r = requests.get(url)
    articles = r.json()['articles']
    return articles, len(articles)


def twitterapi_summaries(query, location):
    try:
        if ' ' in query:
            kw = query.split()
            kw.append(location)
        else:
            kw = list(query)
            kw.append(location)
        tso = TwitterSearchOrder()  # create a TwitterSearchOrder object
        tso.set_keywords(kw)  # let's define all words we would like to have a look for
        tso.set_language('en')  # we want to see German tweets only
        tso.set_count(10)  # we want to see German tweets only
        tso.set_include_entities(False)  # and don't give us all those entity information

        # it's about time to create a TwitterSearch object with our secret tokens
        ts = TwitterSearch(
            consumer_key='We3N5LWOH63onKrHAH0p8oe3I',
            consumer_secret='k4fA8Jxtv6qxl987IlqlX1iWHZGc2nYauoF3Nlg3A7OXwK1yyd',
            access_token='3905868207-FooZNMEk4V1MIMEb6uPvdudIaVaXxyJJGL5iAFr',
            access_token_secret='nbaKLI2IpRpDg9MFM1UISBLFpSdjQYTSISGTPmhxwlnkt'
        )
        news_summaries = []
        # this is where the fun actually starts :)
        n = 0
        for tweet in ts.search_tweets_iterable(tso):
            if n < 10:
                # print('@%s tweeted: %s' % (tweet['user']['screen_name'], tweet['text'], tweet['created_at']))
                news_summaries.append({'user': tweet['user']['screen_name'],
                                       'description': tweet['text'],
                                       'publishTime': tweet['created_at']})
                n += 1
            else:
                break

        return news_summaries, n

    except TwitterSearchException as e:  # take care of all those ugly errors if there are some
        print(e)



import requests


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


def gnewsapi_summaries(query):
    # API_Token = '02bc6d7c6aca458da20650457dd6c934'
    API_Token = 'your token'
    url = 'https://gnews.io/api/v3/search?q={}&token={}'.format(query,API_Token)
    r = requests.get(url)
    articles = r.json()['articles']
    return articles


def twitterapi_summaries(query):
    # to be finished
    pass

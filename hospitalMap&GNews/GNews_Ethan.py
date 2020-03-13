# Author: Yishen Wang
# Data: 2020-03-04


from newsapi import NewsApiClient
import csv

# Init
# https://newsapi.org/docs/get-started
# use limitation and pricing : https://newsapi.org/pricing
newsapi = NewsApiClient(api_key="<user google news API key>")


# output cvs path
OUT_FILE = 'Out_GNews_Ethan.csv'
# Set columns of cvs
fieldIWant = ['source',  'url', 'publishedAt', 'title', 'urlToImage']
# #google news provide 3 request methods:
# 1. top headlines
# top_headlines = newsapi.get_top_headlines(q='Coronavirus',
#                                           sources=None,
#                                           category=None,
#                                           language='en',
#                                           country=None)
#
# 2. everything
# This is the method which I recommend. q = 'keyword(Coronavirus + city)'. sources: newspaper company, ex: bbc, cnn.
# domains:topic ex: market, technology. Return keyword search on page 1.

all_articles = newsapi.get_everything(q='london, Coronavirus',
                                      sources=None,
                                      domains=None,
                                      from_param='2020-03-04',
                                      to='2020-03-01',
                                      language='en',
                                      sort_by='relevancy',
                                      page=1)
# 3. sources
# sources = newsapi.get_sources()


articles = all_articles['articles']

myPois = []

for article in articles:
    myItem = {myKey: article[myKey] for myKey in fieldIWant}
    myPois.append(myItem)
with open(OUT_FILE, 'w') as csvfile:
    # creating a csv dict writer object
    writer = csv.DictWriter(csvfile, fieldnames=fieldIWant)

    # writing headers (field names)
    writer.writeheader()

    # writing data rows
    writer.writerows(myPois)

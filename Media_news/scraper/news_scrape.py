#coding=utf-8
import requests
from bs4 import BeautifulSoup, element
import time
from random import randint
import urllib
import datetime
from datetime import date, timedelta
from selenium import webdriver


def scrape_news_summaries(s, location):
    time.sleep(randint(0, 2))  # setup a limit
    s = s + ' ' + location
    r = requests.get("http://www.google.com/search?q="+s+"&tbm=nws")
    content = r.content
    news_summaries = []
    soup = BeautifulSoup(content, "html.parser")
    st_divs = soup.findAll("div", {"class": "ZINbbc xpd O9g5cc uUPGi"})

    for st_div in st_divs:
        source = st_div.find("div", {"class": "BNeawe UPmit AP7Wnd"}).text
        title = st_div.find("div", {"class": "BNeawe vvjwJb AP7Wnd"}).text
        url = st_div.find('a').attrs['href'].replace('/url?q=', '').split('&')[0]

        publishtime = st_div.find("div", {"class": "BNeawe s3v9rd AP7Wnd"}).text.split(' · ')[0]
        content = st_div.find("div", {"class": "BNeawe s3v9rd AP7Wnd"}).text.split(' · ')[1]
        record = {'source': source,
                  'title': title,
                  'content': content,
                  'url': url,
                  'publishTime': publishtime,
                  }
        news_summaries.append(record)
    return news_summaries, len(news_summaries)


def scrape_baidu_news_summaries(s, location):
    time.sleep(randint(0, 2))  # setup a limit
    s = s + ' ' + location
    # word = '新冠肺炎'
    url = 'https://www.baidu.com/s?rtt=1&bsst=1&cl=2&tn=news&rsv_dl=ns_pc&word=' + urllib.parse.quote(s)
    response = urllib.request.urlopen(url)
    content = response.read()
    news_summaries = []
    soup = BeautifulSoup(content, "html.parser")

    st_divs = soup.findAll("div", {"class": "result"})

    for st_div in st_divs:
        tagp = st_div.find("p", {"class": "c-author"})
        source = tagp.text.split()[0]
        publishtime = ' '.join(tagp.text.split()[1:])
        tagh3 = st_div.find("h3")
        url =  tagh3.find('a').get('href')

        title = tagh3.text.replace('/n', '').strip()
        summary = st_div.find("div", {"class": "c-summary c-row"})
        content = "".join([t for t in summary.contents if type(t) == element.NavigableString]).strip()
        imgurl = ''
        if content == '':
            imgurl = summary.find('img', {"class": "c-img c-img6"}).get('src')
            summary = st_div.find("div", {"class": "c-span18 c-span-last"})
            content = "".join([t for t in summary.contents if type(t) == element.NavigableString]).strip()

        record = {'source': source,
                  'title': title,
                  'content': content,
                  'url': url,
                  'publishTime': publishtime,
                  'Thumbnail': imgurl
                  }
        news_summaries.append(record)
    return news_summaries, len(news_summaries)


def scrape_weibo_news_summaries(s, location):
    time.sleep(randint(0, 2))  # setup a limit
    s = s + ' ' + location
    s = '新冠肺炎 北京'
    url = 'https://s.weibo.com/article?q=' + urllib.parse.quote(s)
    r = requests.get(url)
    response = urllib.request.urlopen(url)
    content = response.read()
    article_content = r.text
    news_summaries = []
    soup = BeautifulSoup(article_content, "html.parser")

    st_divs = soup.findAll("div", {"class": "card-wrap"})
    print(len(st_divs))
    i = 0

    for st_div in st_divs:
        print(i)
        par = st_div.find_parent('div')
        i += 1
        tagh3 = st_div.find("h3")
        url = tagh3.find('a').get('href')


        title = tagh3.find('a').get('title')
        print(title)
        summary = st_div.find("div", {"class": "content"})
        content = summary.find('p').text
        imgurl = summary.find('img').get('src')
        div = summary.find("div", {"class": "act"}).find("div")
        print(soup.findAll('span', recursive=False))
        print(len(soup.findAll('span', recursive=False)))
        spans = summary.findAll('span')
        '''
        spans2 = soup.span#.find(text=True, recursive=False)
        source = spans[0].find('a').text
        publishtime = spans[1].text

        record = {'source': source,
                  'title': title,
                  'content': content,
                  'url': url,
                  'publishTime': publishtime,
                  'Thumbnail': imgurl
                  }
        news_summaries.append(record)
        '''
    return news_summaries, len(news_summaries)


def scrape_twitter_news_summaries(s, location):
    s = s.replace(' ', '+') + '+' + location
    start_date = datetime.datetime.strftime(datetime.datetime.now() - timedelta(1), '%Y-%m-%d')
    url = "https://twitter.com/search?q=" + s + "+since%3A{}".format(start_date)
    options = webdriver.ChromeOptions()
    options.add_argument(
        'user-agent = Chrome/80.0.3987.106')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    # options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=options,
                              executable_path=r'.\chromedriver.exe')
    driver.get(url)
    try:
        tweet_divs = driver.page_source
        obj = BeautifulSoup(tweet_divs)
        content = obj.find_all("div", class_="content")
        # print(content)

        news_summaries = []
        for c in content[:10]:
            tweets = c.find("p", class_="tweet-text").strings
            tweet_text = "".join(tweets)
            tweet_text2 = c.find("p", class_="TweetTextSize js-tweet-text tweet-text").text.split('pic.twitter')[0]
            # content2 = "".join([t for t in tweet_text2.contents if type(t) == element.NavigableString]).strip()
            # print(tweet_text)
            # print("-----------")
            try:
                name = (c.find_all("strong", class_="fullname")[0].string).strip()
            except AttributeError:
                name = "Anonymous"
            date = (c.find_all("span", class_="_timestamp")[0].string).strip()
            url = 'https://twitter.com' + c.find('a', class_="tweet-timestamp").get('href')
            username = c.find_all("span", class_="username")[0].text
            try:
                img = c.find('div', class_='AdaptiveMedia-photoContainer').get('data-image-url')
            except:
                img = None
            actions = c.findAll('span', class_='ProfileTweet-actionCountForAria')
            n_comm = actions[0].text.split()[0]
            n_share = actions[1].text.split()[0]
            n_like = actions[2].text.split()[0]
            # print(tweet_text)
            record = {'tweet_url': url,
                      'name': name,
                      'username': username,
                      'published_date': date,
                      'tweet_description': tweet_text2,
                      'tweet_image': img,
                      'number_comments': n_comm,
                      'number_shares': n_share,
                      'number_likes': n_like,
                      }
            news_summaries.append(record)
        driver.quit()
        return news_summaries, len(news_summaries)
    except Exception as e:
        print("Something went wrong!")
        print(e)
        driver.quit()



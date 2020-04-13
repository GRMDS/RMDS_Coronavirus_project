from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from io import BytesIO
from newsapi import NewsApiClient
import pandas as pd
import pymongo
from pymongo import MongoClient
from typing import List

from email_util import AlertEmail, AttachedImage, Addressee, send_emails

METRICS = ['Date', 'Death', 'Confirmed']
INT_METRICS = {'Death', 'Confirmed'}
NEWSPAPER_RESULTS = {}

@dataclass
class User:

    """A user subscribed to alerts."""

    name: str
    email: str
    city: str
    state: str
    country: str


def get_news_results(
    api_key: str,
    city: str,
    state: str,
    country: str,
    article_limit: int = 5
) -> str:
    key = (city, state, country)
    if key in NEWSPAPER_RESULTS:
        return NEWSPAPER_RESULTS[key]

    news_api = NewsApiClient(api_key=api_key)
    articles = news_api.get_everything(q=f'coronavirus+{city}+{state}')['articles'][:article_limit]

    article_template = '<li><a href="{url}" target="_blank">{title}</a></li>'
    articles_html_parts = [
        article_template.format(url=article['url'], title=article['title'])
        for article in articles
    ]
    articles_html = '\n'.join(articles_html_parts)

    news_results = f"""
        <ul>
            {articles_html}
        </ul>
    """

    NEWSPAPER_RESULTS[key] = news_results

    return news_results


def send_alerts_to_subscribers(
    users: List[User],
    sender_name: str,
    sender_email: str,
    smtp_host: str,
    smtp_port: int,
    smtp_username: str,
    smtp_password: str,
    mongodb_host: str,
    mongodb_port: int,
    mongodb_infections_database: str,
    mongodb_infections_collection: str,
    mongodb_username: str,
    mongodb_password: str,
    news_api_key,
):
    if mongodb_username and mongodb_password:
        mongo_client = MongoClient(
            mongodb_host,
            mongodb_port,
            username=mongodb_username,
            password=mongodb_password,
            authSource=mongodb_infections_database,
            authMechanism='SCRAM-SHA-256',
        )
    else:
        mongo_client = MongoClient(mongodb_host, mongodb_port)

    db = mongo_client[mongodb_infections_database]
    collection = db[mongodb_infections_collection]

    now = datetime.now()
    two_weeks_ago = now - timedelta(days=14)

    emails = []
    for user in users:
        query = {
            'Country/Region': user.country,
            'Province/State': user.state,
            'County/City': user.city,
            'Date': {'$gt': two_weeks_ago},
        }

        results = list(collection.find(query).sort('Date', pymongo.DESCENDING))

        if not results:
            print(f'No results found for {user}')
            continue

        image_plot = get_results_plot(user, results)

        email = get_alert_email(
            results,
            user,
            sender_name,
            sender_email,
            image_plot,
            news_api_key,
        )

        emails.append(email)

    send_emails(smtp_host, smtp_port, smtp_username, smtp_password, emails)


def get_results_plot(user: User, results: List[dict]) -> bytes:
    df_dict = defaultdict(list)

    for result in results:
        for metric in METRICS:
            metric_value = result[metric]

            if metric in INT_METRICS:
                metric_value = int(metric_value)

            df_dict[metric].append(metric_value)

    df = pd.DataFrame.from_dict(df_dict)
    df.set_index('Date', inplace=True)
    plot = df.plot(title=f'Covid19 data for {user.city}, {user.state}, {user.country}')

    buf = BytesIO()
    plot.get_figure().savefig(buf, format='png')
    buf.seek(0)

    return buf.read()


def get_alert_email(
    results: List[dict],
    user: User,
    sender_name: str,
    sender_email: str,
    plot: bytes,
    news_api_key: str,
):
    first_name, last_name = user.name.split(' ')
    most_recent = results[0]
    confirmed = int(most_recent['Confirmed'])
    deaths = int(most_recent['Death'])

    attached_plot = AttachedImage(plot, 'png')

    subject_date = most_recent['Date'].strftime('%Y/%m/%d')

    news_results = get_news_results(
        news_api_key,
        user.city,
        user.state,
        user.country,
    )

    html = f"""
    <html>
        <style>
            table {{
              border-collapse: collapse;
            }}
            td, th {{
              border: 1px solid #dddddd;
              text-align: left;
            }}
        </style>
        <body>
            <div>
                <img src="https://grmds.org/sites/default/files/inline-images/rmds_logo_0.png" alt="Covid Cases" title="Covid Cases" style="display:block" width="300" height="143" />
                <br />
                <p>Dear {first_name},</p>
                <p>
                    You’ve signed up to receive alerts for the following location(s): {user.city}.
                    <a href="https://grmds.org/project-coronavirus-alert-form" target="_blank">Click here</a>
                    to change or add a location to your alerts.
                </p>
                <p>
                    RMDS partners with other data and AI companies to provide a comprehensive alert system. Here are the results for {user.city}:
                </p>
                <table>
                    <tr>
                        <th>Total infections, Infection rate</th>
                        <th>{confirmed}</th>
                    </tr>
                    <tr>
                        <th>Total deaths, Mortality rate</th>
                        <th>{deaths}, {round((deaths / confirmed) * 1000) / 10}%</th>
                    </tr>
                </table>

                <img src="cid:{attached_plot.cid[1:-1]}" alt="Covid Cases" title="Covid Cases" style="display:block" width="640" height="480" />
            </div>
            <hr />
            <p>
                Read news and social media results for your cities selected:
                {news_results}
            </p>
            <p>Powered by NewsAPI.org</p>
            <hr />
            <p>
            RMDS is the one stop shop for our data and AI community to find resources related to COVID-19. Explore the following dashboards to see the distribution of the virus and other epidemiological factors from different perspectives.
                <ul>
                    <li><a href="https://grmds.org/coronavirus/" target="_blank">RMDS Covid19 dashboard</a></li>
                    <li><a href="https://coronavirus.jhu.edu/map.html" target="_blank">John Hopkins Dashboard</a></li>
                </ul>
            </p>
            <hr />
            <p>
	        Copyright © 2020 GRMDS, All Rights Reserved.
                You are receiving this email alert because you opted in via our <a href="https://grmds.org/" target="_blank">website.</a>
            </p>
            <p>
                This email was sent to {user.email}
            </p>
            <p>
                Unsubscribe
            </p>
            <p>
                GRMDS, 225 S lake Ave Fl 3, Pasadena, CA 91101-3009, USA
            </p>
        </body>
    </html>
    """

    email = AlertEmail(
        images=[attached_plot],
        subject=f'Covid19 results in {user.city} for {subject_date}',
        sender=Addressee(sender_name, sender_email),
        recipient=Addressee(user.name, user.email),
        plain_text=f'Confirmed cases: {confirmed} Deaths: {deaths}',
        html=html,
    )

    return email

# The purpose of this notebook is as follows :
# 1. Create a function to scrap world population from wikipedia
# 
# 2. Create a function to insert world population dictionary to Mongodb
#
# 3. Create a function to combine previous two functions and make this process reproducible 


from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import pandas as pd
import argparse
from collections import defaultdict
import csv
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pymongo import MongoClient
import requests
from typing import Dict, List
import pycountry

BASE_URL = 'https://en.wikipedia.org/wiki/'
PATH = 'List_of_countries_by_population_(United_Nations)'
ATTRIBUTES = ['Country', 'Region', 'Population']
GRANULARITY = 'country'



def extract_world_pop(url="https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"):
    '''
    Extract world population table from wikipedia
    Input: wikipedia url
    Output: a dictionary contains population information 
    '''
    html = urlopen(url)
    soup = BeautifulSoup(html)
    table = soup.find("table", {'class':'nowrap'})
    
    ### Country name
    name = table.find_all("span",{'class':'datasortkey'})
    name_list = []
    for i in name:
        name_i = (re.findall(r'data-sort-value=\"(.*?)\"',str(i)))[0]
        if name_i == "Guernsey":
            name_i = "Guernsey and Jersey"
        name_list.append(name_i)
    name_list.remove('Jersey')
    
    ### Population
    table_nocomma = str(table).replace(',', '')
    pop = re.findall(r'<td>(\d+)</td>', table_nocomma)
    pop_list = []
    for i in range(len(pop)):
        if i%2==0:
            pop_list.append(pop[i+1])
            
    ### Region
    region = re.findall(r'\">(\w+)</a>', table_nocomma)
    region_list = []
    for i in region:
        if i in ["Asia", "Americas", "Oceania", "Africa", "Europe"]:
            region_list.append(i)
    pop_df = pd.DataFrame(columns = ["Country", "Region","Population"])
    pop_df['Country'] = name_list
    pop_df['Region'] = region_list
    pop_df["Population"]=pop_list
    pop_dict = pop_df.to_dict('records')
    return pop_dict



def insert_countries_into_db(
    countries: dict,
    mongodb_host: str,
    mongodb_port: int,
    mongodb_dest_database: str,
    mongodb_dest_collection: str,
    mongodb_username: str,
    mongodb_password: str,
):
    '''
    This function takes world population dictionary and insert onto Mongodb
    Input: dictionary of world population and MongoDB credentials
    Output: incert dictionary to Mongodb corresponding collection
    '''
    if mongodb_username and mongodb_password:
        mongo_client = MongoClient(
            mongodb_host,
            mongodb_port,
            username=mongodb_username,
            password=mongodb_password,
            authSource=mongodb_dest_database,
            authMechanism='SCRAM-SHA-256',
        )
    else:
        mongo_client = MongoClient(mongodb_host, mongodb_port)

    db = mongo_client[mongodb_dest_database]
    collection = db[mongodb_dest_collection]

    # We are replacing the entire dataset each time this script is run
    collection.drop()

    collection.insert_many( countries)

def get_country_data(
    url: str,
    mongodb_host: str,
    mongodb_port: int,
    mongodb_dest_database: str,
    mongodb_dest_collection: str,
    mongodb_username: str,
    mongodb_password: str,):
    '''
    This function takes wikipedia url and Mongodb credentials
    Call extract_world_pop to scrap world population dataset from wikipedia
    Call insert_countries_into_df to insert scrapped dataset into Mongodb
    '''
    
    data_dict = extract_world_pop("https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)")
    
    insert_countries_into_db(
    data_dict,
    mongodb_host,
    mongodb_port,
    mongodb_dest_database,
    mongodb_dest_collection,
    mongodb_username,
    mongodb_password,
    )
    
 
'''
insert country level Stringency Index (quantified policy score) from Oxford Univ
https://www.bsg.ox.ac.uk/sites/default/files/Calculation%20and%20presentation%20of%20the%20Stringency%20Index.pdf
Use pycountry to covert alpha_3 country code to country name
insert to new collection country_stringency
'''
def insert_country_stringency(enddate: str, 
    mongodb_host: str,
    mongodb_port: int,
    mongodb_dest_database: str,
    mongodb_dest_collection: str,
    mongodb_username: str,
    mongodb_password: str,):
    
    response = requests.get('https://covidtrackerapi.bsg.ox.ac.uk/api/stringency/date-range/2020-02-01/'+enddate)
    data = list(response.json()['data'].values())
    list_data = []
    for elem in data:
        temp = list(elem.values())
        for elem2 in temp:
            elem2['date_value'] = datetime.strptime(elem2['date_value'], '%Y-%m-%d')
            country = pycountry.countries.get(alpha_3 = elem2['country_code'])
            
            # HK, Macon, Taiwan belong to China
            if country!=None and country not in ['Taiwan', 'Macao', 'Hong Kong']:
                elem2['country'] = country.name
                list_data.append(elem2)
    
    mongo_client = MongoClient(
            mongodb_host,
            mongodb_port,
            username=mongodb_username,
            password=mongodb_password,
            authSource=mongodb_dest_database,
            authMechanism='SCRAM-SHA-256',
        )
    db = mongo_client[mongodb_dest_database]
    collection = db[mongodb_dest_collection]
    
    collection.drop()

    collection.insert_many(list_data)
    
    return list_data
    
    
    

if __name__ == '__main__':
    '''
    parser = argparse.ArgumentParser(description='Pulls wikipedia world population data to find population distribution by countries')
    
    parser.add_argument('--mongodb_host', help='The hostname of the mongodb server', default='localhost')
    parser.add_argument('--mongodb_port', help='The port to connect through for the mongodb server', type=int, default=27017)
    parser.add_argument('--mongodb_dest_database', help='The database to store the country demographics data in', default='COVID19-DB')
    parser.add_argument('--mongodb_dest_collection', help='The collection to store the country demographics data in', default='World_population')
    parser.add_argument('--mongodb_username', help='The username of the mongodb instance', default=None)
    parser.add_argument('--mongodb_password', help='The password of the mongodb instance', default=None)
    
    get_country_data(**vars(parser.parse_args()))
    '''
    x = insert_country_stringency('2020-04-14', '3.101.18.8', 27017, 'COVID19-DB', 'Country_stringency', 'Your Username', 'Your Password')
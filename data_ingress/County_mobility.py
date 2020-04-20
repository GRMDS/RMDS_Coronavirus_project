# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 14:53:00 2020

@author: jidong
"""

from pymongo import MongoClient
import pandas as pd


def get_data_from_url(url):
    data = pd.read_csv(url)
    data = data[data['admin_level'] == 2][['date', 'country_code', 'admin1', 'admin2', 'samples', 'm50', 'm50_index']]
    data.columns = ['date', 'country_name', 'state_name', 'county_name', 'sample_size', 'distance_median', 'percent_of_normal']
    data['date']= pd.to_datetime(data['date']) 
    data = data.to_dict(orient = 'records')
    return data


def insert_mobility_to_mongo(data, mongodb_host: str,
    mongodb_port: int,
    mongodb_dest_database: str,
    mongodb_dest_collection: str,
    mongodb_username: str,
    mongodb_password: str,):
    
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
    count = 0
    for elem in data:
        count +=1
        if count%5000==0:
            print (count)
        elem['county_name'] = elem['county_name'].replace(" County", "")
        collection.update_one({"$and": [{"Date": {'$eq': elem['date']}}, 
                                                 {"Province/State": {'$eq': elem['state_name']}}, 
                                                 {"County/City": {'$eq': elem['county_name']}}]},
                                       {"$set": {"Mobility_sample_size": elem['sample_size'],
                                                 "m50_distance_median_miles": elem['distance_median'],
                                                 "m50_percent_of_normal": elem['percent_of_normal']}})
    
    return



if __name__ == '__main__':
    x = get_data_from_url('https://raw.githubusercontent.com/descarteslabs/DL-COVID-19/master/DL-us-mobility-daterow.csv')
    insert_mobility_to_mongo(x, '3.101.18.8', 27017, 'COVID19-DB', 'CDC-TimeSeries', 'ruser', 'flzx3qc')

# -*- coding: utf-8 -*-
"""
Created on Thr Apr 9 16:31:22 2020

@author: jidong
Merge US community survey data into MongoDB
"""

import pymongo
from pymongo import MongoClient
import numpy as np
import requests
import pandas as pd

BASE_URL = 'https://api.census.gov'
PATH = 'data/2018/acs/acsse'
PATH2 = 'data/2019/pep/population'
ATTRIBUTES = ['name', 'K200201_001E', 'K200201_002E', 'K200201_003E', 'K200201_004E', 'K200201_005E', 
              'K200201_006E', 'K200201_007E','K200103_001E','K201703_001E','K201703_002E','K201703_007E', 'K200301_003E', 'K200301_001E']
ATTRIBUTES2 = ['name', 'density']
ATTRIBUTES_LABEL = ['name','race_total','White', 'Black or African American', 'American Indian and Alaska Native',
                    'Asian', 'Native Hawaiian and Other Pacific Islander', 'Some other race', 'Median age',
                    'poverty_total','below poverty level','above poverty level']
GRANULARITY = 'county'


def get_json_from_api():
    params = {
        'get': ','.join([attr.upper() for attr in ATTRIBUTES]),
        'for': f'{GRANULARITY}:*',
    }
    response = requests.get(url=f'{BASE_URL}/{PATH}', params=params)
    county_data = response.json()
    return county_data

def insert_data(data, mongodb_host: str,
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
    '''
    collection.update_many({},
                      {"$set": {"white_rate": None, "black_rate": None, 
                                "AIAN": None, "asian_rate": None, "NHPI": None, 
                                "other_race": None, "median_age": None, "below_poverty": None,
                                "above_poverty": None, "Hispanic_Latino": None}},
                      upsert=False, array_filters=None)
    
    '''
    for elem in data:
        countyname = elem[0].split(', ')[0]
        statename = elem[0].split(', ')[1]
        if elem[1]!=None:
            white_rate = float(elem[2])/float(elem[1])
            black_rate = float(elem[3])/float(elem[1])
            AIAN = float(elem[4])/float(elem[1])
            asian_rate = float(elem[5])/float(elem[1])
            NHPI = float(elem[6])/float(elem[1])
            other = float(elem[7])/float(elem[1])
        else:
            white_rate, black_rate, AIAN, asian_rate, NHPI, other = [None]*6
        
        median_age = float(elem[8])
        if elem[9]!=None:
            below_poverty = float(elem[10])/float(elem[9])
            above_poverty = float(elem[11])/float(elem[9])
        else:
            below_poverty, above_poverty = None, None
        
        if elem[13]!=None:
            Hispanic_Latino = float(elem[12])/float(elem[13])
        else:
            Hispanic_Latino = None
            
        collection.update_one({"$and": [{"state_name": {"$eq": statename}},{"county_name": {"$eq": countyname}}]},
                              {"$set": {"white_rate": white_rate, "black_rate": black_rate, 
                               "AIAN": AIAN, "asian_rate": asian_rate, "NHPI": NHPI, 
                               "other_race": other, "median_age": median_age, "below_poverty": below_poverty,
                               "above_poverty": above_poverty, "Hispanic_Latino": Hispanic_Latino}},
                              upsert=False)
        

    return collection
    

def insert_landarea(mongodb_host: str,
    mongodb_port: int,
    mongodb_dest_database: str,
    mongodb_dest_collection: str,
    mongodb_username: str,
    mongodb_password: str,):
    
    params = {
        'get': ','.join([attr.upper() for attr in ATTRIBUTES2]),
        'for': f'{GRANULARITY}:*',
    }
    
    response = requests.get(url=f'{BASE_URL}/{PATH2}', params=params)
    land_data = response.json()
    
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
    
    land_data = land_data[1:]
    for elem in land_data:
        countyname = elem[0].split(', ')[0]
        statename = elem[0].split(', ')[1]
        if elem[1]!=None:
            density = float(elem[1])
        else:
            density = None
            
        collection.update_one({"$and": [{"state_name": {"$eq": statename}},{"county_name": {"$eq": countyname}}]},
                              {"$set": {"population_density_people/mi^2": density}},
                              upsert=False)    
        
    return land_data


def insert_beds_data(mongodb_host: str,
    mongodb_port: int,
    mongodb_dest_database: str,
    mongodb_dest_collection: str,
    mongodb_username: str,
    mongodb_password: str,):
    
    bed_data = pd.read_csv('https://raw.githubusercontent.com/GRMDS/RMDS_Coronavirus_project/master/analytics/Shen/Hospital_beds.csv')
    ICU_data = pd.read_csv('https://raw.githubusercontent.com/GRMDS/RMDS_Coronavirus_project/master/analytics/Shen/ICU_beds.csv')
    bed_data.columns = ['statename','countyname','numbeds']
    ICU_data.columns = ['statename','countyname','ICUbeds','population_larger_60']
    bed_data['countyname'] = bed_data['countyname'].str.lower()
    ICU_data['countyname'] = ICU_data['countyname'].str.lower()
    data = ICU_data.merge(bed_data, how = 'left', on = ['statename','countyname'])
    
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
    
    collection.update_many({},
                      {"$set": {"ICUbeds": None, "population_older_60": None, 
                                "num_of_beds": None}},
                      upsert=False, array_filters=None)
    
    for index,row in data.iterrows():
        statename = row.statename
        countyname = row.countyname
        str_list = countyname.split(' ')
        countyname = ''
        for elem in str_list:
            countyname += elem.capitalize()+' '
        countyname = countyname[:-1]
        collection.update_one({"$and": [{"state_name": {"$eq": statename}},{"county_name": {"$eq": countyname}}]},
                              {"$set": {"ICUbeds": row.ICUbeds, "population_older_60": row.population_larger_60, 
                                        "num_of_beds": row.numbeds}},
                              upsert=False) 
    return data


if __name__ == '__main__':
    #x = get_json_from_api()
    #y = insert_data(x[1:], '3.101.18.8', 27017, 'COVID19-DB', 'counties', 'Your Username', 'Your Password')
    #z = insert_landarea('3.101.18.8', 27017, 'COVID19-DB', 'counties', 'Your Username', 'Your Password')
    #t = insert_beds_data('3.101.18.8', 27017, 'COVID19-DB', 'counties', 'Your Username', 'Your Password')
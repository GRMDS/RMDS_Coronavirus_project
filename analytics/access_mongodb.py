#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 15:54:30 2020

From Sam Ko https://github.com/GRMDS/RMDS_Coronavirus_project/blob/master/analytics/sam/Update_CDC.py
"""
#pip install pymongo

import pandas as pd
import pymongo
import warnings
warnings.filterwarnings("ignore")

def mongodb_import(collection_name):
    """
    Import the database from MongoDB and put it into a dataframe. 
    The exact name of the database has to be know to call the function.
    Currently, the collections in the MongoDB are as follows: 'CDC-TimeSeries', 'DXY-TimeSeries', 'World_population', 'counties', 'county_mobility'
    
    """
    
    auth = "mongodb://analyst:grmds@3.101.18.8/COVID19-DB"
    db_name = 'COVID19-DB'
    
    client = pymongo.MongoClient(auth) # defaults to port 27017
    db = client[db_name]
    cdc_ts = pd.DataFrame(list(db[collection_name].find({})))
    return cdc_ts

counties_static_df = mongodb_import('counties')


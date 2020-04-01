# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 16:31:22 2020

@author: jidong
"""
import pymongo
from pymongo import MongoClient
import numpy as np


class Mongo_connector(object):
    def __init__(self, server_ip, user, pw, table):
        self.mongo_client = MongoClient(server_ip + ':27017',
                            username=user,
                            password=pw,
                            authSource='COVID19-DB',
                            authMechanism='SCRAM-SHA-256')
        self.data = self.mongo_client["COVID19-DB"][table]
        
    def get_states_data(self,countryname, statename, lastn):
        docs = self.data.find({"$and": [{"Country/Region": {"$eq": countryname}},
                                {"Province/State": {"$eq": statename}}]}).sort("Date", pymongo.DESCENDING).limit(lastn)
        number = []
        dateList = []
        for doc in docs:
            update_date = doc.get("Date")
            date_obj = update_date.date()
            date_str = date_obj.isoformat()
            dateList.append(date_str)
            number.append([doc.get("Confirmed"), doc.get("Death")])
        dateList.reverse()
        number.reverse()
        number = np.array(number, dtype = 'float')
        return dateList, number
        
        
        


if __name__ == "__main__":
    con = Mongo_connector('3.101.18.8', 'analyst', 'grmds', 'CDC-TimeSeries')
    date, number = con.get_states_data("US","California",10)
    
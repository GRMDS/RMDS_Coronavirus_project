# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 15:16:35 2020

@author: jidong
"""

import pandas as pd
import json
from urllib.request import urlopen, quote
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from statsmodels.tsa.stattools import acf, pacf
from hmmlearn.hmm import GaussianHMM


def get_sequence(province):
    url = 'https://lab.isaaclin.cn/nCoV/api/area?latest=0&province='+quote(province)
    req = urlopen(url)
    res = req.read().decode() 
    temp = json.loads(res)
    return temp


def fetch_city(datapath, city):
    with open(datapath) as json_file:
        data = json.load(json_file)
        
    citylist = []
    for i in data["results"]:
        try:
            for cc in i['cities']:
                if cc['cityName'] == city:
                    citylist.append({**{'updateTime': datetime.fromtimestamp(i['updateTime'] // 1000).strftime("%m/%d/%Y")}, **cc})
        except Exception as e:
            print (e)
    data = pd.DataFrame.from_dict(citylist, orient = 'columns')
    data.drop_duplicates(subset=['updateTime'], keep='first', inplace=True)
    data = data.iloc[::-1].reset_index().drop(columns=['index'])
    return data

def calculate_rate(citydata, totalpopulation):
    citydata.loc[:,'susceptible'] = totalpopulation-citydata['confirmedCount']
    citydata.loc[:,'infectious'] = citydata['confirmedCount'] - citydata['curedCount'] - citydata['deadCount']
    #citydata[['susceptible','infectious','curedCount','deadCount']].plot.line()
    data = citydata[['susceptible','infectious','curedCount','deadCount','confirmedCount']].to_numpy()
    mu = []
    for i in range(1,len(data)):
        mu_SI = (data[i][4]-data[i-1][4])/data[i][0]
        mu_IR = (data[i][2]-data[i-1][2])/data[i][1]
        mu_ID = (data[i][3]-data[i-1][3])/data[i][1]
        mu.append([mu_SI, mu_IR, mu_ID])
    delta = []
    for i in range(1,len(data)):
        delta_SI = max(data[i][4]-data[i-1][4],0)
        delta_IR = max(data[i][2]-data[i-1][2],0)
        delta_ID = max(data[i][3]-data[i-1][3],0)
        S = data[i][0]
        I = data[i][1]
        delta.append([delta_SI, delta_IR, delta_ID, S, I])
    return np.array(mu), np.array(delta)



def get_time():
    return

def hmmmodel(seq):
    model = GaussianHMM(n_components=2, n_iter=1000)
    model.fit(seq)
    hidden_states = model.predict(seq)
    return model, hidden_states
    


if __name__ == "__main__":
    #data = get_sequence('广东省')
    data = fetch_city('guangdongdata.txt','深圳')
    mu, delta = calculate_rate(data, 12530000)
    hmm, hidden_states = hmmmodel(np.reshape(delta[:,0],[len(delta[:,0]),1]))
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 10:28:10 2020

@author: jidong
"""
import pandas as pd
import numpy as np
from scipy import stats
import torch.tensor
from model import datasets
from torch.utils.data import random_split


def get_ts_dxy(skip_day):
    data = pd.read_csv("https://raw.githubusercontent.com/BlankerL/DXY-COVID-19-Data/master/csv/DXYArea.csv")
    searchfor = ['外地来','明确地区','不明地区','未知地区','未知','人员','待明确']
    data = data[~data['cityName'].str.contains('|'.join(searchfor))]
    data = data[~data['provinceName'].str.contains('|'.join(['香港','台湾','澳门']))]
    data = data[data['cityName'].groupby(data['cityName']).transform('size')>40]
    data['updateTime']=pd.to_datetime(data['updateTime']).dt.date
    grouped = data.sort_values('updateTime',ascending = False).groupby(['updateTime'])
    i = 0
    integrate = pd.DataFrame()
    for name,group in grouped:
        i +=1
        set_group = group.drop_duplicates(['provinceName','cityName'])
        set_group = set_group[['provinceName','cityName','city_confirmedCount','city_curedCount','city_deadCount']]
        set_group.rename(columns={"city_confirmedCount": "city_confirmedCount"+' '+str(name), 
                                  "city_curedCount": "city_curedCount"+' '+str(name),
                                  'city_deadCount': 'city_deadCount'+' '+str(name)}, inplace=True)
        if i<=skip_day:
            integrate = set_group
        else:
            integrate = integrate.merge(set_group, how = 'outer', on = ['provinceName','cityName'])
    integrate.dropna(thresh=len(integrate.columns)*0.9, inplace = True)
    integrate['ts']= integrate.iloc[:,2:].values.tolist()
    integrate = integrate[['provinceName','cityName','ts']].reset_index(drop=True)
    return integrate

def calculate_graph(data,first_level_city_list):
    graph = []
    for index, row in data.iterrows():
        if row.provinceName.endswith('市'):
            neilist_1 = data.index[data['provinceName'].str.contains('市')].tolist()
            neilist_2 = data.index[data['cityName'].str.contains('|'.join(first_level_city_list))].tolist()
            graph.append(neilist_1+neilist_2)
        elif row.cityName in first_level_city_list:
            neilist_1 = data.index[data['provinceName'].str.contains('市')].tolist()
            neilist_2 = data.index[data['cityName'].str.contains('|'.join(first_level_city_list))].tolist()
            neilist_3 = data.index[data['provinceName'] == row.provinceName].tolist()
            graph.append(list(set(neilist_1+neilist_2+neilist_3)))
        else:
            neilist_1 = data.index[data['provinceName'] == row.provinceName].tolist()
            graph.append(neilist_1)
    return graph

def prepare_data(data,window):
    arraydata = []
    for index, row in data.iterrows():
        ts = np.diff(np.reshape(row.ts,(-1,3)),axis = 0)
        ts = ts[~np.isnan(ts).any(axis=1),:]
        for i in range(len(ts)-window+1):
            seq = ts[i:i+window]
            seq = np.nan_to_num(stats.zscore(seq, axis = 0))
            arraydata.append(seq)
    arraydata = torch.tensor(arraydata, dtype=torch.float)
    #split or not
    dataset = datasets(arraydata)
    train_len = int(dataset.__len__()*0.8)
    test_len = dataset.__len__()-train_len
    train_data, test_data = random_split(dataset,[train_len,test_len])
    return train_data, test_data
            




if __name__ == "__main__":
    data = get_ts_dxy(1)
    first_level_city_list = ['郑州','杭州','乌鲁木齐','南京','贵阳','合肥','青岛','济南',
                             '厦门','昆明','南昌','兰州','长春','西安','福州','哈尔滨',
                             '长沙','深圳','广州','成都','武汉','太原','桂林','石家庄','银川',
                             '三亚','海口','沈阳','大连']
    #graph = calculate_graph(data, first_level_city_list)
    train,test = prepare_data(data,8)
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 10:38:09 2020

@author: jidong
"""
import torch
from model import LSTMModel
from util import get_ts_dxy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
from util import get_location_using_baidu



def evaluation(provincename, cityname, modelpath, data):
    lat, long = get_location_using_baidu(provincename+cityname)
    Mymodel = LSTMModel(1, 100, 1, 100)
    Mymodel.load_state_dict(torch.load(modelpath))
    series = data.loc[(data["provinceName"] == provincename) & (data["cityName"] == cityname), "ts"].values.tolist()
    series = np.reshape(series,(-1,3))
    if np.isnan(series[-1][0]):
        series = series[:-1]
    diff_series = np.diff(series,axis = 0)
    n = len(diff_series)
    predict_series = np.array(series[0:7,0:1])
    store_diff = np.array(diff_series[0:7,0:1])
    for i in range(n-7):
        seq = np.array(diff_series[i:i+7])
        total_recover = np.sum(seq[:,1])
        total_death = np.sum(seq[:,2])
        seq = seq[:,0:1]
        mean = np.mean(seq[:,0],axis = 0)
        std = np.std(seq[:,0],axis = 0)
        seq -= mean
        if std!=0:
            seq /= std
        tensor_seq = torch.tensor(seq, dtype=torch.float, requires_grad=False)
        add_seq = torch.tensor([[lat], [long], [total_recover], [total_death], [mean], [std]])
        tensor_seq = torch.cat([tensor_seq,add_seq])
        tensor_seq.resize_(1, 13, 1)
        predictions = np.array(Mymodel(tensor_seq).tolist()[0])
        real_diff = predictions * std + mean
        store_diff = np.append(store_diff,[real_diff],axis = 0)
        if i>=n-7:
            print (diff_series)
            print ([real_diff[0],0,0])
            diff_series = np.append(diff_series,[real_diff[0],0,0],axis = 0)
            predict_series = np.append(predict_series,[np.array(list(map(sum,zip(predict_series[-1],real_diff))))],axis = 0)
        else:
            predict_series = np.append(predict_series,[np.array(list(map(sum,zip(series[i+6][0:1],real_diff))))],axis = 0)
    return series, predict_series, provincename+cityname, store_diff, diff_series

def draw_plot(origin,pred,title):
    fontP = font_manager.FontProperties()
    fontP.set_family('SimHei')
    fontP.set_size(14)
    
    x1 = origin[:,0]
    x2 = pred[:,0]
    plt.plot(x1, label = "True_value")
    plt.plot(x2, label = "Predicted_value")
    plt.xlabel('Time (days)')
    plt.ylabel('Infections')
    plt.title(title,fontproperties=fontP)
    plt.legend()
    plt.grid(True)
    plt.show()
    return




if __name__ == "__main__":
    modelpath = 'Trained_model/trained_model_5100.pkl'
    wholedata = get_ts_dxy(1)
    origin , predictions, title, store_diff, diff_series  = evaluation('陕西省', '西安', modelpath, wholedata)
    draw_plot(origin , predictions, title)
    draw_plot(diff_series, store_diff, title+'difference')
    
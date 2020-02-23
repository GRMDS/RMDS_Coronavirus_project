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



def evaluation(provincename, cityname, modelpath, data):
    Mymodel = LSTMModel(3, 150, 1, 3)
    Mymodel.load_state_dict(torch.load(modelpath))
    series = data.loc[(data["provinceName"] == provincename) & (data["cityName"] == cityname), "ts"].values.tolist()
    series = np.reshape(series,(-1,3))
    if np.isnan(series[-1][0]):
        series = series[:-1]
    diff_series = np.diff(series,axis = 0)
    n = len(diff_series)
    seq = []
    predict_series = []
    predict_series[:] = series[0:7]
    store_diff = []
    store_diff[:] = diff_series[0:7]
    for i in range(n):
        seq[:] = diff_series[i:i+7]
        mean = np.mean(seq,axis = 0)
        std = np.std(seq,axis = 0)
        seq -= mean
        seq /= std
        tensor_seq = torch.tensor(np.nan_to_num([seq]), dtype=torch.float, requires_grad=False)
        predictions = np.array(Mymodel(tensor_seq).tolist()[0])
        real_diff = predictions * std + mean
        store_diff = np.append(store_diff,[real_diff],axis = 0)
        if i>=n-7:
            diff_series = np.append(diff_series,[real_diff],axis = 0)
            predict_series = np.append(predict_series,[np.array(list(map(sum,zip(predict_series[-1],real_diff))))],axis = 0)
        else:
            predict_series = np.append(predict_series,[np.array(list(map(sum,zip(series[i+6],real_diff))))],axis = 0)
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
    modelpath = 'trained_model_3300.pkl'
    wholedata = get_ts_dxy(1)
    origin , predictions, title, store_diff, diff_series  = evaluation('江苏省', '南京', modelpath, wholedata)
    draw_plot(origin , predictions, title)
    draw_plot(diff_series, store_diff, title+'difference')
    
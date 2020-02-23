# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 16:41:01 2020

@author: jidong
"""
import torch
from model import LSTMModel
from torch.utils.data import DataLoader
from util import get_ts_dxy, prepare_data
import torch.nn as nn

def training_model(train_data, test_data, num_epochs, batch_size=8, input_dim=3, hidden_dim=150, output_dim=3, seq_dim=7):
    
    train_loader = DataLoader(dataset=train_data, batch_size=batch_size, shuffle=True, drop_last=True)
    test_loader = DataLoader(dataset=train_data, batch_size=batch_size, shuffle=True, drop_last=True)
    Mymodel = LSTMModel(input_dim, hidden_dim, 1, output_dim)
    loss_function = nn.MSELoss()
    optimizer = torch.optim.Adam(Mymodel.parameters(), lr=0.01)
    iters = 0
    for epoch in range(num_epochs):
        for data_val,target in train_loader:
            # clean the previous gredient
            optimizer.zero_grad()
            outputs = Mymodel(data_val)
            #calculate loss
            loss = loss_function(outputs, target)
            # using loss to calculate gredient, stored in model
            loss.backward()
            # using gredient to update model parameters
            optimizer.step()
            iters += 1
            if iters % 300 ==0:
                for test_val,test_target in test_loader:
                    test_outputs = Mymodel(test_val)
                    loss2 = loss_function(test_outputs, test_target)
                print('Iteration: {}. TrainLoss: {}. TestLoss: {}'.format(iters, loss.item(), loss2.item()))
                torch.save(Mymodel.state_dict(), 'trained_model_'+ str(iters) + '.pkl')
    return Mymodel


def prediction(Mymodel,seq):
    return
                    
if __name__ == "__main__":
    data = get_ts_dxy(1)
    train,test = prepare_data(data,8)
    Mymodel = training_model(train,test, num_epochs = 10)
        
    
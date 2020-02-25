# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 16:09:51 2020

@author: jidong
"""

import torch
import torch.nn as nn
from torch.utils.data import Dataset 

class LSTMModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, layer_dim, output_dim):
        super(LSTMModel, self).__init__()
        self.hidden_dim = hidden_dim
        self.layer_dim = layer_dim
        # batch_first=True causes input/output tensors to be of shape
        # (batch_dim, seq_dim, feature_dim)
        self.lstm = nn.LSTM(input_dim, hidden_dim, layer_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)
        self.fc2 = nn.Linear(output_dim+2, 1)
        self.relu = nn.PReLU()
        #self.fc3 = nn.Linear(100,1)

    def forward(self, x):
        # Initialize hidden state
        h0 = torch.zeros(self.layer_dim, x.size(0), self.hidden_dim, dtype=torch.float).requires_grad_()
        # Initialize cell state
        c0 = torch.zeros(self.layer_dim, x.size(0), self.hidden_dim, dtype=torch.float).requires_grad_()
        out, (hn, cn) = self.lstm(x[:,0:7,:], (h0.detach(), c0.detach()))
        # Index hidden state of last time step
        out = torch.cat((out[:,-1,:],x[:,11:,0]), dim = 1)
        #out = self.fc(out[:,-1,:])
        #out = self.relu(self.fc(out[:, -1, :]))
        #out = torch.cat((out,x[:,7:,0]), dim = 1)
        out = self.fc2(out)
        #out = self.fc3(out)
        return out
    
    
class datasets(Dataset):
    def __init__(self, data):
        self.data = data
        
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, index):
        target = self.data[index][7]
        data_val = torch.cat([self.data[index][0:7], self.data[index][8:]])
        data_val.resize_(13, 1)        
        target.resize_(1)
        return data_val,target
    
    
if __name__ == "__main__":
    print (LSTMModel(1,100,1,6))
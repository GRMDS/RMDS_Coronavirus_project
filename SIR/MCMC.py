# -*- coding: utf-8 -*-
"""
Created on Thu Feb 27 11:19:20 2020

@author: jidong
"""



import pymc3 as pm
from analysis import fetch_city,calculate_rate,hmmmodel
import numpy as np
import matplotlib.pyplot as plt


def simulation(data, prior1, prior2, seg, totalpopulation):
    real_infected = np.array(data['confirmedCount'] - data['curedCount'] - data['deadCount'])
    S = totalpopulation - data['confirmedCount'][0]
    R = data['curedCount'][0]
    D = data['deadCount'][0]
    simulated = []
    simulated.append(real_infected[0])
    i = 1
    while simulated[-1]>0:
        if i<seg:
            prior = prior1
        else:
            prior = prior2
        P_SI = np.random.choice(prior['P_SI'])
        #P_IR = np.random.choice(prior['P_IR'])
        #P_ID = np.random.choice(prior['P_ID'])
        index = np.random.choice(len(prior))
        P_IRD = prior[index]['P_IRD']
        N_SI = np.random.binomial(S, P_SI)
        #N_IR = np.random.binomial(simulated[i-1], P_IR)
        #N_ID = np.random.binomial(simulated[i-1], P_ID)
        N_IRD = np.random.multinomial(simulated[i-1], P_IRD)
        S -= N_SI
        R += N_IRD[1]
        D += N_IRD[2]
        simulated.append(simulated[i-1]+N_SI-N_IRD[1]-N_IRD[2])
        i += 1
        if i>200:
            break
    return real_infected, simulated

def draw_plot(origin,pred,title):

    x1 = origin
    x2 = pred
    plt.plot(x1, label = "True_value")
    plt.plot(x2, label = "Predicted_value")
    plt.xlabel('Time (days)')
    plt.ylabel('Infections')
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()
    return

if __name__ == "__main__":
    
    data = fetch_city('guangdongdata.txt','深圳')
    mu, delta = calculate_rate(data, 12530000)
    hmm, hidden_states = hmmmodel(np.reshape(delta[:,0],[len(delta[:,0]),1]))
    seg = np.where(np.roll(hidden_states,1)!=hidden_states)[0][1]
        
    basic_model1 = pm.Model()
    basic_model2 = pm.Model()
    n = len(delta)
    with basic_model1:
            #Lambda = pm.Normal('lambda', mu=0, tau = 1e-4)
            #gamma = pm.Normal('gamma', mu=0, tau=1e-4)
            #tau = pm.Normal('tau', mu=0, tau=1e-4)
            #p1 = pm.Deterministic('P_SI', 1-pm.math.exp(-Lambda))
            #p2 = pm.Deterministic('P_IR', 1-pm.math.exp(-gamma))
            #p3 = pm.Deterministic('P_ID', 1-pm.math.exp(-tau))
        p1 = pm.Beta('P_SI', alpha = 0.5, beta = 0.5)
        p2 = pm.Dirichlet('P_IRD', a=np.ones(3))
        #p2 = pm.Beta('P_IR', alpha = 0.5, beta = 0.5)
        #p3 = pm.Beta('P_ID', alpha = 0.5, beta = 0.5)
        SI = pm.Binomial('SI', n = delta[:seg,3].astype(np.int32), p = p1, observed=delta[:seg,0])
        IRD = pm.Multinomial('IRD', n = delta[:seg,4].astype(np.int32), p = p2, observed = np.stack((delta[:seg,4]-delta[:seg,1]-delta[:seg,2],delta[:seg,1],delta[:seg,2]), axis=-1))
        #IR = pm.Binomial('IR', n = delta[:,4].astype(np.int32), p = p2, observed=delta[:,1])
        #ID = pm.Binomial('ID', n = delta[:,4].astype(np.int32), p = p3, observed=delta[:,2])
        
        #step = pm.NUTS()        
        trace1 = pm.sample(2000, pm.Metropolis(), cores=1, chains = 2, init='advi+adapt_diag', tune=500)
            
    with basic_model2:
        p1 = pm.Beta('P_SI', alpha = 0.5, beta = 0.5)
        p2 = pm.Dirichlet('P_IRD', a=np.ones(3))
        SI = pm.Binomial('SI', n = delta[seg:,3].astype(np.int32), p = p1, observed=delta[seg:,0])
        IRD = pm.Multinomial('IRD', n = delta[seg:,4].astype(np.int32), p = p2, observed = np.stack((delta[seg:,4]-delta[seg:,1]-delta[seg:,2],delta[seg:,1],delta[seg:,2]), axis=-1))
        trace2 = pm.sample(2000, pm.Metropolis(), cores=1, chains = 2, init='advi+adapt_diag', tune=500)
    
    pm.traceplot(trace1 , varnames = ['P_SI'])
    pm.plot_posterior(trace1, varnames = ['P_SI'])
    
    pm.traceplot(trace2 , varnames = ['P_SI'])
    pm.plot_posterior(trace2, varnames = ['P_SI'])
    
    real, results = simulation(data, trace1, trace2, seg, 12530000)
    draw_plot(real,results[:-1],'simulation')





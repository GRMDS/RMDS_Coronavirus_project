# -*- coding: utf-8 -*-
"""
Created on Tue Mar 31 11:12:42 2020

@author: jidong
"""

from mongodata import Mongo_connector
import numpy as np
import pymc3 as pm
import pandas as pd
import logging
from scipy.stats import sem, t
from scipy import mean
import matplotlib.pyplot as plt


def CI(confidence, data):
    n = len(data)
    m = mean(data)
    std_err = sem(data)
    h = std_err * t.ppf((1 + confidence) / 2, n - 1)
    lower = m - h
    upper = m + h
    return lower, upper


def draw_plot(origin,pred,lower,upper,title):
    x1 = origin
    x2 = pred
    plt.plot(x1, label = "True_value")
    plt.plot(x2, 'c--', label = "Predicted_value")
    plt.plot(lower, 'r--', label = '95%_CI_lower')
    plt.plot(upper, 'r--', label = '95%_CI_upper')
    plt.xlabel('Time (days)')
    plt.ylabel('Infections')
    plt.title(title)
    plt.legend()
    plt.grid(True)
    #plt.savefig('simulation.png')
    plt.show()
    return



class SIR_model(object):
    def __init__(self, r0_mean, gamma_mean):
        self.r0 = r0_mean
        self.gamma = gamma_mean
        self.trace = []
        self.simulation = []
        self.popu = 0
        self.data = []


    def SIR_training(self, sequence, totalpopulation):
        self.popu = totalpopulation
        self.data = sequence[:]
        acc_infect = sequence[:,0] / totalpopulation
        basic_model = pm.Model()
        n = len(acc_infect)
        I = acc_infect[0]
        R = 0
        S = 1-I
        with basic_model:
            BoundedNormal = pm.Bound(pm.Normal, lower=0.0, upper=1.0)
            BoundedNormal2 = pm.Bound(pm.Normal, lower=1.0,upper=10.0)
            theta = []
            r0 = BoundedNormal2('R_0', mu = self.r0, sigma = 0.72)
            gamma = BoundedNormal('gamma', mu = self.gamma , sigma = 0.02)
            beta = pm.Deterministic('beta', r0*gamma)
            ka = pm.Gamma('ka', 2, 0.0001)
            Lambda1 = pm.Gamma('Lambda1', 2, 0.0001)
            qu = pm.Uniform('qu', lower = 0.1, upper = 1.0)
            
            theta.append(pm.Deterministic('theta_'+str(0), pm.math.stack([S, I, R])))
            for i in range (1,n):
                states = theta[i-1]
                solve_theta = pm.Deterministic('solve_theta_'+str(i), ka*pm.math.stack([states[0]-qu*beta*states[0]*states[1], 
                                               states[1]+qu*beta*states[0]*states[1]-gamma*states[1], 
                                                states[2] + gamma*states[1]]))
                theta.append(pm.Dirichlet('theta_'+str(i), a = solve_theta, shape = (3)))
                real_infect = pm.Beta('real_infect_'+str(i), Lambda1*theta[i][1], Lambda1*(1-theta[i][1]), observed = acc_infect[i])
    
            step = pm.Metropolis()
            Trace = pm.sample(2000, cores=16, chains = 1, init='auto', step = step)
            self.trace = Trace
            #pm.plot_posterior(self.trace, varnames = ['R_0', 'gamma', 'qu'])
     
    def one_simulation(self, totalday):
        if self.trace==[]:
            print ('Please train model first')
            return
        simulated = []
        real = self.data[:,0]
        n = len(real)
        i = 0
        Trace = self.trace
        k = np.random.randint(100,2000)
        while i<totalday:
            if i<n:
                theta = Trace[k]['theta_'+str(i)]
                simulated.append(theta[1]*self.popu)
                i += 1
            else:
                ka = Trace[k]['ka']
                Lambda = Trace[k]['Lambda1']
                gamma = Trace[k]['gamma']
                beta = Trace[k]['beta']
                qu = Trace[k]['qu']
                solve_theta = ka*np.array([theta[0]-qu*beta*theta[0]*theta[1], 
                                               theta[1]+qu*beta*theta[0]*theta[1]-gamma*theta[1], 
                                                theta[2] + gamma*theta[1]])
                if solve_theta[1]<=5/self.popu:
                    break
                theta = np.random.dirichlet(alpha = solve_theta)
                while theta[1]==0:
                    theta = np.random.dirichlet(alpha = solve_theta)
                pred_infect = np.random.beta(a = Lambda*theta[1], b = Lambda*(1-theta[1]))
                simulated.append(pred_infect*self.popu)
                i += 1
                
        return simulated
        
    def pred_sample(self, nsample, totalday):
        total_results = np.zeros((nsample, totalday))
        for i in range(nsample):
            results = self.one_simulation(totalday)
            for j in range(len(results)):
                total_results[i,j] = results[j]
        self.simulation = total_results
        average = np.mean(total_results, axis = 0)
        lower = []
        upper = []
        for i in range(totalday):
            l,u = CI(0.95, total_results[:,i])
            lower.append(l)
            upper.append(u)
        
        draw_plot(self.data[:,0], average,lower,upper, 'simulation')
        

if __name__ == "__main__":
    logger = logging.getLogger('pymc3')
    logger.setLevel(logging.ERROR)
    con = Mongo_connector('3.101.18.8', 'analyst', 'grmds', 'CDC-TimeSeries')
    model = SIR_model(2.15, 1/17)
    date, number = con.get_states_data("US","California",7)
    model.SIR_training(number, 39512223)
    model.pred_sample(10000, 200)



# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 16:10:16 2020

@author: jidong
"""
import pandas as pd


def task(date, number):
    most_recent_infect = number[-1][0]
    most_recent_d = number[-1][1]
    delta_infect = number[-1][0] - number[-2][0]
    three_day_acc = ((number[-1][0] - 2*number[-2][0] + number[-3][0])/2 + 
                     (number[-2][0] - 2*number[-3][0] + number[-4][0])/2 + 
                     (number[-3][0] - 2*number[-4][0] + number[-5][0])/2)/3
    mortality_rate = most_recent_d / most_recent_infect
    return most_recent_infect, most_recent_d, delta_infect, three_day_acc, mortality_rate, date[-1]

def search_loc_based_on_zipcode(zipcode):
    data = pd.read_excel('zipcodes.xlsx')
    for index,row in data.iterrows():
        code = str(row['zio_code_starting_with'])
        if str(zipcode).startswith(code):
            return row['States']
    
    return 'Unavailable'




if __name__ == "__main__":
    state = search_loc_based_on_zipcode('91106')
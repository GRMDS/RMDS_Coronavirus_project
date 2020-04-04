# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 20:26:47 2020

@author: jidong
"""

from flask import Flask
from mongodata import Mongo_connector
from pipeline_util import task, search_loc_based_on_zipcode
from flask import jsonify


app = Flask(__name__)

@app.route('/get_statistics/<int:zipcode>')
def update_recommendation(zipcode):
    con = Mongo_connector('3.101.18.8', 'analyst', 'grmds', 'CDC-TimeSeries')
    state = search_loc_based_on_zipcode(str(zipcode))
    date, number = con.get_states_data("US",state,7)
    results = task(date, number)
    
    
    
    return jsonify(
        State = state,
        Most_recent_infecious = results[0],
        Most_recent_deaths = results[1],
        Infecious_change = results[2],
        Three_day_acc = results[3],
        Mortality_rate = results[4],
        Update_time = results[5]
    )

    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)


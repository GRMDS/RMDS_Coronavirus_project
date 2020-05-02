#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
from datetime import datetime
import folium
from folium.plugins import MarkerCluster
import warnings
warnings.filterwarnings("ignore")


def import_county():
    """
    This function imports data from MongoDB 'CDC-TimeSeries' collection and creates a dataframe that only holds US data to the county level. 
    
    I have added 2 extra columns (Confirmed_New and Death_New) that show the count of new cases/deaths each day
    since the original data only has the cumulative number. 
    
    I think this function would help you jump into your county-level data analysis right away.
    
    """
    import pymongo
    from pymongo import MongoClient
    import pandas as pd
    
    auth = "mongodb://analyst:grmds@3.101.18.8/COVID19-DB"
    db_name = 'COVID19-DB'
    
    client = pymongo.MongoClient(auth) # defaults to port 27017
    db = client[db_name]
    cdc_ts = pd.DataFrame(list(db['CDC-TimeSeries'].find({})))
    
    
    US = cdc_ts.loc[cdc_ts['Country/Region'] == 'US']
    US = US.loc[US['County/City'] != ""]
    US = US.sort_values(by=['Province/State', 'County/City', 'Date']).reset_index(drop = True)
    US = US.drop(['Country/Region'], axis=1)
    
    US['Confirmed'] = US['Confirmed'].astype(int)
    US['Death'] = US['Death'].astype(int)

    US['Confirmed_New'] = US.groupby(['Province/State','County/City'])['Confirmed'].diff().fillna(0)
    US['Death_New'] = US.groupby(['Province/State','County/City'])['Death'].diff().fillna(0)

    col_name="Date"
    col = US.pop(col_name)
    US.insert(0, col_name, col)
    
    col_name="Confirmed_New"
    col = US.pop(col_name)
    US.insert(7, col_name, col)
    
    col_name="Death_New"
    col = US.pop(col_name)
    US.insert(9, col_name, col)
   
    return US


def top10_county():
    """
    From the US dataframe created above, this fuction
    - identifies top 10 counties with the most number of infections, which is defined by the most total number of infections on the most recent day
    - adds a new column 'Days After 100th Infection' that shows the number of days before/after 100th confirmed case 
    
    """
        
    county = import_county()
    county['state_county'] = county['County/City'] + ", " + county['Province/State'] 

    last_date = max(np.unique(county["Date"].dt.strftime('%Y-%m-%d')).tolist())
    today = county.loc[(county['Date'] == last_date)]
    today.sort_values(by = 'Confirmed', ascending = False, inplace=True)
    top10 = today.head(10)
    top10_list = top10.state_county.tolist()

    top10 = county.loc[(county.state_county == top10_list[0])]
    for x in top10_list[1:]:
        top10 = pd.concat([top10, county.loc[(county.state_county == x)]])

    top10.reset_index(drop = True, inplace= True)   
    
    threshold = 100
    
    
    top10_list = top10.state_county.unique().tolist()
    date_list = top10["Date"].dt.strftime('%Y-%m-%d').unique().tolist()

    county_name = []
    over_threshold = []

    for county in top10_list:
        for date in date_list:
            if top10.loc[(top10['Date'] == date) & (top10['state_county'] == county)].Confirmed.values[0] > threshold:
                over_threshold.append(date)
                county_name.append(county)
                break

    over_threshold = [datetime.strptime(x, '%Y-%m-%d') for x in over_threshold]

    top10['Days After 100th Infection'] =''

    for x in range(0,len(county_name)):
        for i in range(0,len(top10)):
            infection_date = over_threshold[x]
            if top10.iloc[i,14] == county_name[x] and top10.iloc[i,0] == infection_date:
                top10.iloc[i,15] = 1
            elif top10.iloc[i,14] == county_name[x] and top10.iloc[i,0] >= infection_date:
                top10.iloc[i,15] = top10.iloc[i-1,15] + 1
            elif top10.iloc[i,14] == county_name[x] and top10.iloc[i,0] < infection_date:
                top10.iloc[i,15] = (top10.iloc[i,0] - over_threshold[x]).days
    
    return top10



def top10_infection_plot():
    """
    Plots Date vs Daily number of new infections for Top 10 counties
    
    """
    
    top10 = top10_county()
    county_list = top10.state_county.unique().tolist()
    
    plt.figure(figsize = (16,8))
    for i in county_list:
        county = top10[top10.state_county == i]
        plt.plot("Date", "Confirmed_New", data = county, label = i)
        plt.title("Number of Infections per Day by Top 10 Counties", size = 15)
        plt.xlabel("Date")
        plt.ylabel("Number of Infections")
        plt.legend(loc=2)
    plt.grid()
    plt.show()
     
    
def top10_cml_infection_plot():
    """
    Plots Date vs Cumulative number of infections for Top 10 counties
    
    """
    
    top10 = top10_county()
    county_list = top10.state_county.unique().tolist()

    plt.figure(figsize = (16,8))
    for i in county_list:
        county = top10[top10.state_county == i]
        plt.plot("Date", "Confirmed", data = county, label = i)
        plt.title("Cumulative Number of Infections per Day by Top 10 Counties", size = 15)
        plt.xlabel("Date")
        plt.ylabel("Total Number of Infections")
        plt.legend(loc=2)
    plt.grid()
    plt.show()
    
    
    
def top10_after100_plot():
    
    """
    Plots Days after 100th case vs Daily number of new infections for Top 10 counties
    """
    
    top10 = top10_county()
    county_list = top10.state_county.unique().tolist()

    plt.figure(figsize = (16,8))
    for i in county_list:
        county = top10[top10.state_county == i]
        plt.plot("Days After 100th Infection", "Confirmed_New", data = county, label = i)
        plt.title("Number of Infections by Top 10 Counties", size = 15)
        plt.xlabel("Days Since 100th Infection")
        plt.ylabel("Number of Infections")
        plt.legend(loc=2)
    plt.grid()
    plt.show()
    
    
    
def top10_after100_cml_plot():
    
    """
    Plots Days after 100th case vs Cumulative number of infections for Top 10 counties
    """
    
    top10 = top10_county()
    county_list = top10.state_county.unique().tolist()

    plt.figure(figsize = (16,8))
    for i in county_list:
        county = top10[top10.state_county == i]
        plt.plot("Days After 100th Infection", "Confirmed", data = county, label = i)
        plt.title("Cumulative Number of Infections by Top 10 Counties", size = 15)
        plt.xlabel("Days Since 100th Infection")
        plt.ylabel("Total Number of Infections")
        plt.legend(loc=2)
    plt.grid()
    plt.show()



    
    
def most_recent():
    county = import_county()
    county['state_county'] = county['County/City'] + ", " + county['Province/State'] 
    last_date = max(np.unique(county["Date"].dt.strftime('%Y-%m-%d')).tolist())
    today = county.loc[(county['Date'] == last_date)]
    return today


def hotspots():
    """
       Identifies 'hotspots', or top 20 counties with the most number of confirmed cases for the most recent date
       """

    category = 'Confirmed'
    number = 20

    county = import_county()
    county['state_county'] = county['County/City'] + ", " + county['Province/State']

    last_date = max(np.unique(county["Date"].dt.strftime('%Y-%m-%d')).tolist())
    today = county.loc[(county['Date'] == last_date)]
    today.sort_values(by=category, ascending=False, inplace=True)
    top = today.head(number)
    top_list = top.state_county.tolist()

    top = county.loc[(county.state_county == top_list[0])]
    for x in top_list[1:]:
        top = pd.concat([top, county.loc[(county.state_county == x)]])

    top.reset_index(drop=True, inplace=True)

    threshold = 100

    top_list = top.state_county.unique().tolist()
    date_list = top["Date"].dt.strftime('%Y-%m-%d').unique().tolist()

    county_name = []
    over_threshold = []

    for county in top_list:
        for date in date_list:
            if top.loc[(top['Date'] == date) & (top['state_county'] == county)].Confirmed.values[0] > threshold:
                over_threshold.append(date)
                county_name.append(county)
                break

    over_threshold = [datetime.strptime(x, '%Y-%m-%d') for x in over_threshold]

    top['Days After 100th Infection'] = ''

    for x in range(0, len(county_name)):
        for i in range(0, len(top)):
            infection_date = over_threshold[x]
            if top.iloc[i, 14] == county_name[x] and top.iloc[i, 0] == infection_date:
                top.iloc[i, 15] = 1
            elif top.iloc[i, 14] == county_name[x] and top.iloc[i, 0] >= infection_date:
                top.iloc[i, 15] = top.iloc[i - 1, 15] + 1
            elif top.iloc[i, 14] == county_name[x] and top.iloc[i, 0] < infection_date:
                top.iloc[i, 15] = (top.iloc[i, 0] - over_threshold[x]).days

    top_today = top.loc[(top['Date'] == last_date)]

    return top_today


def hotspot_map():
    hotspot = hotspots()
    hotspot.reset_index(drop = True, inplace= True)
    hotspot['Longitude'] = pd.to_numeric(hotspot['Longitude'],errors='coerce')
    hotspot['Latitude'] = pd.to_numeric(hotspot['Latitude'],errors='coerce')
    
    locations = hotspot[['Latitude', 'Longitude']]
    locationlist = locations.values.tolist()
    

    map2 = folium.Map(location=[39.8283, -98.5795], zoom_start=4)

    marker_cluster = MarkerCluster().add_to(map2)

    for point in range(0, len(locationlist)):
        name = hotspot.loc[point,['state_county']].values[0]
        rank = 'Rank: ' + str(point)
        confirmed = 'Confirmed: ' + str(hotspot.loc[point,['Confirmed']].values[0])

        folium.Marker(locationlist[point], 
                      popup=(name, rank, confirmed), 
                      icon = folium.Icon(color='red')).add_to(marker_cluster)

    recent = most_recent()
    recent['Longitude'] = pd.to_numeric(recent['Longitude'],errors='coerce')
    recent['Latitude'] = pd.to_numeric(recent['Latitude'],errors='coerce')
    recent = recent.dropna(subset=['Longitude']) 
    recent = recent.dropna(subset=['Latitude'])
    recent.reset_index(drop = True, inplace= True) 

    locations = recent[['Latitude', 'Longitude']]
    locationlist = locations.values.tolist()
    
    for point in range(0, len(locationlist)):
        name = recent.loc[point,['state_county']].values[0]
        confirmed = recent.loc[point,['Confirmed']].values[0]
        size = (confirmed + 1000).astype(float)

        folium.Circle(radius = size,
                      location = locationlist[point],popup=(name, str(confirmed)),
                      color = 'crimson',
                      fill = True).add_to(map2)
    
    return map2



if __name__ == '__main__':

    import_county()
    top10_county()
    top10_infection_plot()
    top10_cml_infection_plot()
    top10_after100_plot()
    top10_after100_cml_plot()
    hotspot_map()


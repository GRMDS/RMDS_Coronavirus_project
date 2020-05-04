# The purpose of this notebook is as follows :
# 1. Create a function to retrice an excel file through a website
# 
# 2. Clean the data based on the retrived file
#
# 3. Compile output data in appopriate format for MongoDB inserting


import pandas as pd
from sodapy import Socrata
import json
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import requests
import re
import webbrowser
import numpy as np


# In[2]:


pattern = r'.*xlsx'
BASE_URL = "https://www.bea.gov"
site ="https://www.bea.gov/data/income-saving/personal-income-county-metro-and-other-areas"
hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
req = Request(site,headers=hdr)
page = urlopen(req)
soup = BeautifulSoup(page)


# In[3]:


def get_excel (site, pattern):
    files = str(soup.find('a',attrs={'href':re.compile(pattern)}))
    path = re.findall(pattern,files)[0][9:]
    url=BASE_URL+path
    return url


# In[4]:


url = get_excel(site, pattern)



# In[6]:


data = pd.read_excel('lapi1119.xlsx').iloc[4:-3,[0,3]]
data.columns=['County','2018 Personal Income Per Capita']
data = data.reset_index().iloc[:,1:]
df_list = np.split(data, data[data.isnull().all(1)].index) 
df_list[1] = df_list[1].dropna()
state = df_list[1].County.tolist()[0]
df_final=pd.DataFrame()
for i in range(1,len(df_list)):
    df_list[i]=df_list[i].dropna()
    state = df_list[i].County.tolist()[0]
    df_list[i]['State']=state
    df_list[i]=df_list[i][df_list[i].County!=state]
    df_final = pd.concat([df_final,df_list[i]],axis=0)


# In[7]:


df_final.to_csv('income_county.csv')

if __name__ == '__main__':
    x = get_excel(site, pattern)


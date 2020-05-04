#!/usr/bin/env python
# coding: utf-8

# In[25]:


import pandas as pd
from sodapy import Socrata
import json
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re


# In[82]:


pattern = r'.*xlsx'
site ="https://www.bea.gov/data/income-saving/personal-income-county-metro-and-other-areas"
hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
req = Request(site,headers=hdr)
page = urlopen(req)
soup = BeautifulSoup(page)


# In[114]:


def get_excel (site, pattern):
    files = str(soup.find('a',attrs={'href':re.compile(pattern)}))
    excel = re.findall(pattern,files)
    return excel

if __name__ == '__main__':
    x= get_excel(site, pattern)


# In[115]:


get_excel(site, pattern)


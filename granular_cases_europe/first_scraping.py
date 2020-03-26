## DO NOT RUN!!!
##
## This file contains the code used to extract the data for the first time
## to create the csv files for the following countries:
##    - Spain
##    - Italy
##    - France 

## Libraries
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import re
import tabula
import ssl
import PyPDF2
import io
import requests
from datetime import datetime
from time import sleep

ssl._create_default_https_context = ssl._create_unverified_context

###   SPAIN   ##############################################
############################################################
## A daily report in pdf is in the url:
## https://www.mscbs.gob.es/profesionales/saludPublica/ccayes/alertasActual/nCov-China/documentos/Actualizacion_{no}_COVID-19.pdf
## Where {no} is the report number. First public report is online from 31
## when they found 1 case in La Gomera from 31.01, one from Mallorca, one
## in Tenerife, 2 in Madrid, 1 in Castellon and 1 in Barcelona.
## total of 8 by 26.02.2020. From here only text
## Report No. 35 (3.03.2020) is the first one with a table per province
## and a similar Table for Italy. We can start from here

def Spain_get_table (no):
    """
Extracts data from the report number<no> obtained from the Health 
department of spain (www.mscbs.gob.es).

Returns the data, as extracted, as pd.dataframe
    """
    URL = f"https://www.mscbs.gob.es/profesionales/saludPublica/ccayes/alertasActual/nCov-China/documentos/Actualizacion_{no}_COVID-19.pdf"
    ## Extract all tables 
    tables = tabula.read_pdf(URL, pages = "all", multiple_tables = True)
    ## Iterate over all tables and find our target table
    for df in tables:
        for col in df:
            if type(df[col][1]) == str:
                bool_list = df[col].str.contains('Asturias')
                for element in bool_list:
                    if element == True:
                        target = df
    ## <target? contains our data
    try:
        target
    except NameError:
        print("Table not found")
        sys.exit(1)
    ## Get timestamp
    r = requests.get(URL, verify=False)
    f = io.BytesIO(r.content)
    reader = PyPDF2.PdfFileReader(f)
    contents = reader.getPage(0).extractText()
    contents = re.sub('\n', '', contents)
    match = re.search(r'\d{2}.\d{2}.\d{4}', contents)
    if match is None:
        match = re.search(r'\d{1}.\d{2}.\d{4}', contents)
    if match is None:
        print("Date not found")
        date = 'NaN'
    else:
        date = datetime.strptime(match.group(), '%d.%m.%Y').date()
    target['Timestamp'] = date
    return(target)

## BUG
spain35 = Spain_get_table(35) # Did not find the table (which exists)

spain36 = Spain_get_table(36)
spain37 = Spain_get_table(37)
spain38 = Spain_get_table(38)
spain39 = Spain_get_table(39)
spain40 = Spain_get_table(40)
spain41 = Spain_get_table(41)
spain42 = Spain_get_table(42)
spain43 = Spain_get_table(43)

spain44 = Spain_get_table(44) # Page not found
spain45 = Spain_get_table(45) # Page not found

spain46 = Spain_get_table(46)
spain47 = Spain_get_table(47)
spain48 = Spain_get_table(48)
## FINAL: make a function to extract the data 

spain_over_time = spain36.append([spain37, spain38, spain39,spain40, spain41, spain42,spain43, spain46, spain47,spain48], ignore_index = True)

list(spain_over_time.columns)

spain = pd.DataFrame({"country":"Spain", "region":spain_over_time["CCAA"], "confirmed_infected":spain_over_time["Total casos"], "dead":spain_over_time["Fallecidos"], "timestamp": spain_over_time["Timestamp"]}) 

#spain.to_csv("./granular_cases_europe/Spain_first.csv", index = False)

###   FRANCE   #############################################
############################################################
## The website provided below contains all the data exactly as we need
## We just need to translate it

dat_raw = pd.read_csv("https://raw.githubusercontent.com/opencovid19-fr/data/master/dist/chiffres-cles.csv")

list(dat_raw.columns)
dat_raw['granularite']

france = pd.DataFrame({"country":"France", "granularity":dat_raw["granularite"], "name":dat_raw["maille_nom"], "confirmed_infected": dat_raw["cas_confirmes"], "dead": dat_raw["deces"], "recovered": dat_raw["reanimation"], "timestamp": dat_raw["date"]})

#france.to_csv("./granular_cases_europe/France_first.csv", index = False)

## Details
## Granularity has several variables, in the order
## World = "monde"
## Country = "pays"
## "departement" and "region": France is divided into 18 regions
##                            (13 metropolitan) and 101 departments 

###   ITALY   ##############################################
############################################################
## Good data is stored in the website:
## https://statistichecoronavirus.it/coronavirus-italia/
## You can choose region in the map or simply add at the end
## https://statistichecoronavirus.it/coronavirus-italia/puglia/
## or choose it from the list in the following link
## https://statistichecoronavirus.it/regioni-coronavirus-italia/
## The last one contains more details per region 

## Getting general data per region 
source_url = "https://statistichecoronavirus.it/regioni-coronavirus-italia/"
driver = webdriver.Firefox(executable_path="./granular_cases_europe/geckodriver")
driver.get(source_url)
content = driver.page_source 
soup = BeautifulSoup(content, "lxml")
driver.quit()

## Extract the table 
table = soup.find('tbody')
links = []
region = []
population = []
for tr in table.find_all("tr"):
    get_url = re.search("(?P<url>https?://[^\s]+)", str(tr)).group()
    get_url = re.sub('[^A-Za-z0-9/\-\:\.]+', '', get_url)
    links.append(get_url)
    raw = [i.text for i in tr.find_all("td")]
    reg = raw[0]
    pop = raw[1]
    region.append(reg)
    population.append(pop)

#on each tr, find td, where data is contained
regioni = pd.DataFrame({"Region":region, "Population":population, "Data_site":links})
## Save regioni, with general info about the regions
#regioni.to_csv('./granular_cases_europe/Italy_regions.csv', index = False)

## Extract data per region 
regioni = pd.read_csv('./granular_cases_europe/Italy_regions.csv')

italy_all = pd.DataFrame()
#for i in range(len(regioni.Region)):
for i in range(len(regioni.Region)):
    URL = regioni.Data_site[i]
    driver = webdriver.Firefox(executable_path="./granular_cases_europe/geckodriver")
    driver.get(URL)
    print('Opening '+regioni.Data_site[i])
    sleep(20)
    content = driver.page_source 
    soup = BeautifulSoup(content, "lxml")
    driver.quit()
    table = soup.find_all("table")
    rows = []
    if len(table) > 1:
        for t in table[1].find_all('tr'):
            rows.append(t.text)
    else:
        print("Table not found for "+regioni.Region[i])
        continue
    rows[0] = "\n"+rows[0]
    rows = [x.replace("\n", "", 1) for x in rows]
    it_data = pd.DataFrame(rows)
    it_data = it_data[0].str.split('\n', 4, expand=True)
    it_data.columns = it_data.iloc[0]
    it_data = it_data.drop([0,1]).reset_index(drop = True)
    it_data["Region"] = regioni.Region[i]
    italy_all = italy_all.append(it_data, ignore_index = True)
    print("Data extraction succesful")

## Last record: 21.03.2020
italy_all = pd.read_csv('./granular_cases_europe/Italy_first.csv')

## Format date 
day = [re.sub('[^A-Za-z0-9]+', '-', x)+'2020' for x in italy_all.Data]
day = [datetime.strptime(x, '%d-%m-%Y').date() for x in day] # Timestamp for df

for col in italy_all:
    if type(italy_all[col][0]) == str:
        italy_all[col] = italy_all[col].str.replace('\((.*)\).*', '')

italy = pd.DataFrame({"country":"Italy", "region":italy_all["Region"], "confirmed_infected": italy_all["Contagi"], "dead": italy_all["Morti"], "recovered": italy_all["Guariti"], "timestamp": day})
#italy.to_csv('./granular_cases_europe/Italy_first.csv', index = False)

Italy = pd.read_csv('./granular_cases_europe/Italy_first.csv')
tt = [dt.datetime.strptime(x, '%d-%m-%Y').date() for x in Italy.timestamp]
Italy['tt'] = tt

###   GERMANY   #############################################
############################################################
#import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import pandas as pd
import datetime as dt
#from selenium.webdriver.common.keys import Keys

region = []
total = []
recovered = []
dead = []
timestamp = []
tody = dt.datetime.today().date()
dia = tody

urlpage = 'https://interaktiv.morgenpost.de/corona-virus-karte-infektionen-deutschland-weltweit/'
driver = webdriver.Firefox(executable_path="./granular_cases_europe/geckodriver")
driver.get(urlpage)
time.sleep(30)
## clik button
driver.find_element_by_class_name('fnktable__expand').click()
time.sleep(5)

## For each click do:
for i in range (1, 55, 1):
    driver.find_element_by_class_name('slider-prev').click()
    print('Loading data')
    time.sleep(5)
    content = driver.page_source 
    soup = BeautifulSoup(content, "lxml")
    table = soup.find_all("tbody")
    dia = tody - dt.timedelta(i)
    ## Withdraw data 
    for t in table[0].find_all('tr'):
        reg = t.find_all('td', {"class":"region"})
        region.append(reg[0].text)
        tot = t.find_all('td', {"class":"confirmed"})
        total.append(tot[0].text)
        rec = t.find_all('td', {"class":"recovered"})
        recovered.append(rec[0].text)
        de = t.find_all('td', {"class":"deaths"})
        dead.append(de[0].text)
        timestamp.append(dia)

driver.quit()
## Clean data 
total = [re.sub('\.', '', x) for x in total]
dead = [re.sub('\.', '', x) for x in dead]
recovered = [re.sub('\.', '', x) for x in recovered]

germany = pd.DataFrame({'country': 'Germany', 'region': region, 'confirmed_infected': total, 'dead':dead, 'recovered':recovered, 'timestamp':timestamp})

#germany.to_csv('./granular_cases_europe/Germany_first.csv', index = False)

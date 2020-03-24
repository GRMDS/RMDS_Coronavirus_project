## Global variables
import pandas as pd
data_sp = pd.read_csv("./granular_cases_europe/Spain.csv")

## Functions
def last_update_text():
    """
Extracts the text with the link to the document from the main website.
Due to problems in the code, we cannot extract directly the link (href),
so we decided to use the report number (Actualizacion no#)
    """
    from selenium import webdriver
    from bs4 import BeautifulSoup
    from time import sleep
    import re
    source_url = "https://www.mscbs.gob.es/profesionales/saludPublica/ccayes/alertasActual/nCov-China/situacionActual.htm"
    driver = webdriver.Firefox(executable_path="./granular_cases_europe/geckodriver")
    driver.get(source_url)
    sleep(20)
    content = driver.page_source 
    soup = BeautifulSoup(content, "lxml")
    text_update = []
    for a in soup.find_all("a", href = True):
        if 'Actualización' in a.text:
            text_update.append(a.text)
            text_update.append(a['href'])
            print("Found: " + text_update[0])
            driver.quit()
    return(text_update)
## Create a global variables with the text 
text_update = last_update_text()

def sp_last_update():
    "Obtains the date of the last official update"
    import re
    from datetime import datetime
    "Obtains the date of the last update"
    global text_update
    match = re.search(r'\d{2}.\d{2}.\d{4}', text_update[0])
    if match is None:
        match = re.search(r'\d{1}.\d{2}.\d{4}', text_update[0])
    if match is None:
        print("Date not found")
        date = 'NaN'
    else:
        date = datetime.strptime(match.group(), '%d.%m.%Y').date()
    return(date)

def sp_compare_update():
    """
Compares if the last update is already in our data base.

    True = Our data base is up to date
    False = We need to get the latest data 
    """
    import pandas as pd
    date = sp_last_update()
    global data_sp
    bol = data_sp['timestamp'].isin([str(date)]).any()
    return(bool(bol))

def sp_get_new():
    """
Extracts the data from the website and process it in the same format as
the previous one, leaving it ready to append
    """
    import re
    import tabula
    import pandas as pd
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
    global text_update
    #text_pre = re.sub(":.*", "", text_update)
    #update_no = re.findall(r'\d+', text_pre)[0]
    URL = re.sub(".*profesionales", "https://www.mscbs.gob.es/profesionales", text_update[1])
    print("Getting data from "+URL)
    ## Extract all tables 
    tables = tabula.read_pdf(URL, pages = "all", multiple_tables = True)
    ## Iterate over all tables and find our target table
    for dframe in tables:
        df = dframe.dropna(how = 'all')
        for col in df:
            if type(df[col][0]) == str:
                for element in df[col]:
                    if type(element) != float:
                        if "Asturias" in element:
                            target = df
                            break #<target> contains our raw data
            break
        break 
    try:
        target
    except NameError:
        print("Table not found")
        sys.exit(1)
    target['Timestamp'] = sp_last_update()
    #return(updated_df)
    return(target)

target = sp_get_new()
updated_data = pd.DataFrame({"country":"Spain", "region":target["CCAA"], "confirmed_infected":target["TOTAL conf."], "dead":target["Fallecidos"], "timestamp": target["Timestamp"]})

def spain_update():
    """
Updates the file named <Spain.csv> if a new entry is found in
the official website:

https://www.mscbs.gob.es/profesionales/saludPublica/ccayes/alertasActual/nCov-China/situacionActual.htm
    """
    if sp_compare_update():
        print("No updates found")
    else:
        global updated_data
        try:
            updated_data
        except NameError:
            print("Problem in table format.\n Run sp_get_new() and check the data from there, or check the source directly")
            sys.exit(1)
        updated_data.to_csv("./granular_cases_europe/Spain.csv", mode = 'a', index = False, header=False)
        print("Following updates added:\n")
        return(data_sp)

## Bug on 22.03.2020
## <sp_get_new()> got headers as first row
## PLUS: Names of some headers changed
## Issue was fixed manually. After few more cases we can asses it better
## Waiting couple of days.
##
#target.loc[0] # contains header (first row)
#list(target.columns) # current column names
#
#target['Timestamp'][0] = 'Timestamp'
#target.columns = target.iloc[0] # New names 
#target = target.drop([0,1]).reset_index(drop = True) # remove row 1
#
#updated_data = pd.DataFrame({"country":"Spain", "region":target["CCAA"], "confirmed_infected":target["TOTAL conf."], "dead":target["Fallecidos"], "timestamp": target["Timestamp"]})

## Bug on 24.03.2020
## BUG in for loop fixed (sp_get_new)
## PLUS: Names of some headers changed
## Idea: Only search for the word "Total" in headers name 

## Global variables
import pandas as pd
data_sp = pd.read_csv("Spain.csv")

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
    driver = webdriver.Firefox(executable_path="./geckodriver")
    driver.get(source_url)
    sleep(20)
    content = driver.page_source 
    soup = BeautifulSoup(content, "lxml")
    for a in soup.find_all("a", href = True):
        if 'Actualización' in a.text:
            text_update = a.text
            print("Found: " + text_update)
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
    match = re.search(r'\d{2}.\d{2}.\d{4}', text_update)
    if match is None:
        match = re.search(r'\d{1}.\d{2}.\d{4}', text_update)
    if match is None:
        print("Date not found")
        date = 'NaN'
    else:
        date = datetime.strptime(match.group(), '%d.%m.%Y').date()
    return(date)

def sp_compare_update():
    """
Compares if the last update is already in our data base.
Retrusn True when it is, and False when it is not.
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
    text_pre = re.sub(":.*", "", text_update)
    update_no = re.findall(r'\d+', text_pre)[0]
    URL = f"https://www.mscbs.gob.es/profesionales/saludPublica/ccayes/alertasActual/nCov-China/documentos/Actualizacion_{update_no}_COVID-19.pdf"
    ## Extract all tables 
    tables = tabula.read_pdf(URL, pages = "all", multiple_tables = True)
    ## Iterate over all tables and find our target table
    for dframe in tables:
        df = dframe.dropna(how = 'all')
        for col in df:
            print(col)
            if type(df[col][0]) == str:
                for element in df[col]:
                    if type(element) != float:
                        if "Asturias" in element:
                            target = df
                            break #<target> contains our raw data
    try:
        target
    except NameError:
        print("Table not found")
        sys.exit(1)
    target['Timestamp'] = sp_last_update()
    updated_df = pd.DataFrame({"country":"Spain", "region":target["CCAA"], "confirmed_infected":target["Total casos"], "dead":target["Fallecidos"], "timestamp": target["Timestamp"]})
    return(updated_df)

def spain_update():
    """
Updates the file named <Spain.csv> if a new entry is found in
the official website:

https://www.mscbs.gob.es/profesionales/saludPublica/ccayes/alertasActual/nCov-China/situacionActual.htm
    """
    if sp_compare_update() == False:
        global data_sp
        updated_sp = sp_get_new()
        data_sp = data_sp.append(updated_sp, ignore_index = True)
        data_sp.to_csv("Spain.csv", index = False)
        return(data_sp)
    else:
        print("No updates found")

def ge_get_soup():
    """
Extracts code from the website

NOTE: The website uses javascript, hence it changes according to the browser and conditions
that the website finds. This code works using Firefox in a full screen mode. Any modification
(i.e. small screen) will alter the functioning.
    """
    from bs4 import BeautifulSoup
    from selenium import webdriver
    import time
    import pandas as pd
    ## Get to the website
    urlpage = 'https://interaktiv.morgenpost.de/corona-virus-karte-infektionen-deutschland-weltweit/'
    driver = webdriver.Firefox(executable_path="./granular_cases_europe/geckodriver")
    driver.get(urlpage)
    time.sleep(30)
    ## clik button to expand table 
    driver.find_element_by_class_name('fnktable__expand').click()
    time.sleep(5)
    content = driver.page_source 
    soup = BeautifulSoup(content, "lxml")
    driver.quit()
    return(soup)

soup = ge_get_soup()

def ge_new_data():
    "Create pd.df with the latest data, except timestamp"
    from bs4 import BeautifulSoup
    import pandas as pd
    global soup
    import re
    ## Extract table data 
    region = []
    total = []
    recovered = []
    dead = []
    table = soup.find_all("tbody")
    for t in table[0].find_all('tr'):
        reg = t.find_all('td', {"class":"region"})
        region.append(reg[0].text)
        tot = t.find_all('td', {"class":"confirmed"})
        total.append(tot[0].text)
        rec = t.find_all('td', {"class":"recovered"})
        recovered.append(rec[0].text)
        de = t.find_all('td', {"class":"deaths"})
        dead.append(de[0].text)
    ## Clean data
    total = [re.sub('\.', '', x) for x in total]
    dead = [re.sub('\.', '', x) for x in dead]
    recovered = [re.sub('\.', '', x) for x in recovered]
    ## Make df
    germany_new = pd.DataFrame({'country': 'Germany', 'region': region, 'confirmed_infected': total, 'dead':dead, 'recovered':recovered})
    return(germany_new)

def ge_day_update():
    "Returns the date of the last update found in the website"
    from bs4 import BeautifulSoup
    from datetime import datetime
    global soup
    last_updt = soup.find('div', {'class':'ticker-timestamp'}).find('strong').text
    date = datetime.strptime(last_updt, '%d.%m.%Y').date()
    return(date)

def germany_update():
    "Updates the file Germany.csv"
    import pandas as pd
    data_ge = pd.read_csv("./granular_cases_europe/Germany.csv")
    new_date = ge_day_update()
    if data_ge['timestamp'].isin([str(new_date)]).any():
        print("No updates found")
    else:
        ge_new = ge_new_data()
        ge_new['timestamp'] = new_date
        ge_new.to_csv("./granular_cases_europe/Germany.csv", mode = 'a', index = False, header=False)
        print("Following updates added:\n")
        return(ge_new)

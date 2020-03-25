def it_get_data():
    """
Obtains new data from the website

https://statistichecoronavirus.it/regioni-coronavirus-italia/
    """
    from selenium import webdriver
    from bs4 import BeautifulSoup
    import pandas as pd
    import re
    from time import sleep
    source_url = "https://statistichecoronavirus.it/regioni-coronavirus-italia/"
    driver = webdriver.Firefox(executable_path="./granular_cases_europe/geckodriver")
    driver.get(source_url)
    sleep(20)
    content = driver.page_source 
    soup = BeautifulSoup(content, "lxml")
    driver.quit()
    ## Extract the table 
    table = soup.find('tbody')
    region = []
    confirmed_infected = []
    dead = []
    recovered = [] 
    for tr in table.find_all("tr"):
        raw = [i.text for i in tr.find_all("td")]
        raw = [re.sub('\.', '', i) for i in raw]
        reg = raw[0]
        con = raw[2]
        de = raw[5]
        rec = raw[6]
        region.append(reg)
        confirmed_infected.append(con)
        dead.append(de)
        recovered.append(rec)
    ## Write df
    new_data = pd.DataFrame({"country": "Italy", "region":region, "confirmed_infected":confirmed_infected, "dead":dead, "recovered":recovered})
    return(new_data)

def it_update_day():
    """
Obtains date of last update from the website

https://statistichecoronavirus.it/coronavirus-italia/
    """
    from selenium import webdriver
    from bs4 import BeautifulSoup
    import pandas as pd
    import re
    from time import sleep
    from datetime import datetime
    source_url = "https://statistichecoronavirus.it/coronavirus-italia/"
    driver = webdriver.Firefox(executable_path="./granular_cases_europe/geckodriver")
    driver.get(source_url)
    sleep(20)
    content = driver.page_source 
    soup = BeautifulSoup(content, "lxml")
    driver.quit()
    ## Extract the table 
    table = soup.find('tbody')
    all_dates = []
    for tr in table.find_all("tr"):
        raw = [i.text for i in tr.find_all("td")]
        dat = raw[0]
        all_dates.append(dat)
    if "aggiornamento" in all_dates[0]:
        date = all_dates[1]+"/2020"
    else:
        date = all_dates[0]+"/2020"
    date = re.sub(' ','', date)
    date = datetime.strptime(date, '%d/%m/%Y').date()
    return(date)
    ## Write df

def italy_update():
    import pandas as pd
    data_it = pd.read_csv("./granular_cases_europe/Italy.csv")
    new_date = it_update_day()
    if data_it['timestamp'].isin([str(new_date)]).any():
        print("No updates found")
    else:
        it_new = it_get_data()
        it_new['timestamp'] = new_date
        it_new.to_csv("./granular_cases_europe/Italy.csv", mode = 'a', index = False, header=False)
        print("Following updates added:\n")
        return(it_new)

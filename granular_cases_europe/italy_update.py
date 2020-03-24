def it_link_update():
    """
Extracts the text with the link to the document from the main website.
Due to problems in the code, we cannot extract directly the link (href),
so we decided to use the report number (Actualizacion no#)
    """
    from selenium import webdriver
    from bs4 import BeautifulSoup
    from time import sleep
    import re
    source_url = "http://www.salute.gov.it/portale/nuovocoronavirus/dettaglioContenutiNuovoCoronavirus.jsp?lingua=italiano&id=5351&area=nuovoCoronavirus&menu=vuoto"
    driver = webdriver.Firefox(executable_path="./granular_cases_europe/geckodriver")
    driver.get(source_url)
    sleep(20)
    content = driver.page_source 
    soup = BeautifulSoup(content, "lxml")
    driver.quit()
    for a in soup.find_all("a", href = True):
        if 'Situazione Italia' in a.text:
            link_update = a['href']
            print("Found: " + link_update)
    return('http://www.salute.gov.it'+link_update)

def it_new_data():
    from tabula import convert_into
    import pandas as pd
    ## Somehow tabula did not manage to extract,
    ## but it can convert into csv directly
    URL = it_link_update()
    convert_into(URL, "./granular_cases_europe/it_tmp.csv", output_format="csv")
    italy_updated = pd.read_csv('./granular_cases_europe/it_tmp.csv', skiprows = 2, thousands = '.')
    totals = [x for x in range(len(italy_updated.iloc[:, 0])) if italy_updated.iloc[:, 0][x] == "TOTALE"]
    italy_updated = italy_updated.drop(range(totals[0], len(italy_updated.iloc[:, 0])))#.reset_index(drop = True)
    italy = pd.DataFrame({"country": "Italy", "region":italy_updated.iloc[:, 0], "confirmed_infected": italy_updated.iloc[:, 7], "dead": italy_updated.iloc[:, 6], "recovered": italy_updated.iloc[:, 5]})
    return(italy)

def it_date_update():
    import pandas as pd
    import re
    from datetime import datetime
    update = pd.read_csv('./granular_cases_europe/it_tmp.csv', nrows = 0)
    update = ''.join(list(update.columns))
    match = re.search(r'\d{2}.\d{2}.\d{4}', update)
    if match is None:
        match = re.search(r'\d{1}.\d{2}.\d{4}', contents)
    if match is None:
        print("Date not found")
        date = 'NaN'
    else:
        date = datetime.strptime(match.group(), '%d/%m/%Y').date()
    return(date)

it_new = it_new_data()

def italy_update():
    import pandas as pd
    data_it = pd.read_csv("./granular_cases_europe/Italy.csv")
    global it_new
    new_date = it_date_update()
    it_new['timestamp'] = new_date
    if data_it['timestamp'].isin([str(new_date)]).any():
        print("No updates found")
    else:
        it_new.to_csv("./granular_cases_europe/Italy.csv", mode = 'a', index = False, header=False)
        print("Following updates added:\n")
        return(it_new)

## BUG 24.03.2020
## Rows were added at the begining as table headers
## That makes the columns to be arranged differently
## Manual fixing by spliting columns:
#import pandas as pd
#italy_updated = pd.read_csv('./granular_cases_europe/it_tmp.csv', skiprows = 7, thousands = '.')
#df2 = italy_updated['positivi'].str.split(' ', 5, expand=True)
#italy_updated = pd.concat([italy_updated, df2], axis = 1)
#totals = [x for x in range(len(italy_updated.iloc[:, 0])) if italy_updated.iloc[:, 0][x] == "TOTALE"]
#italy_updated = italy_updated.drop(range(totals[0], len(italy_updated.iloc[:, 0])))#.reset_index(drop = True)
#it_new = pd.DataFrame({"country": "Italy", "region":italy_updated.iloc[:, 0], "confirmed_infected": italy_updated["Unnamed: 3"], "dead": italy_updated[4], "recovered": italy_updated[3]})

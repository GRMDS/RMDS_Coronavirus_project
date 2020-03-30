def france_update():
    """
Updates the file named <France.csv> if a new info is found in
our target official website:

https://raw.githubusercontent.com/opencovid19-fr/data/master/dist/chiffres-cles.csv
    """
    import pandas as pd
    from time import sleep
    data_fr = pd.read_csv("./granular_cases_europe/France.csv")
    dat_raw = pd.read_csv("https://raw.githubusercontent.com/opencovid19-fr/data/master/dist/chiffres-cles.csv")
    dat_reg = dat_raw.query('granularite == "region"')
    dat_raw = dat_reg.groupby(['date', 'maille_nom']).agg({'cas_confirmes': 'max', 'deces': 'max', 'reanimation':'max'}).reset_index()
    data_imported = pd.DataFrame({"country":"France", "region":dat_raw["maille_nom"], "confirmed_infected": dat_raw["cas_confirmes"], "dead": dat_raw["deces"], "recovered": dat_raw["reanimation"], "timestamp": dat_raw["date"]})
    if data_fr['timestamp'].equals(data_imported['timestamp']):
    ## if this is true, there are no differences (NO UPDATES)
        print("No updates found")
    else:
        data_imported.to_csv("./granular_cases_europe/France.csv", index = False)
        print('Following updates added:\n')
        return(data_fr)

## NOTE: From 25.03.2020 many missing values of confirmed_infected
##       From 27.03.2020 no data for confirmed_infected
## TRY to find another source or contact them and ask

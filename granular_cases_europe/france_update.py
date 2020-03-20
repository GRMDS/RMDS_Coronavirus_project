def france_update():
    """
Updates the file named <France.csv> if a new info is found in
our target official website:

https://raw.githubusercontent.com/opencovid19-fr/data/master/dist/chiffres-cles.csv
    """
    import pandas as pd
    data_fr = pd.read_csv("France.csv")
    data_raw = pd.read_csv("https://raw.githubusercontent.com/opencovid19-fr/data/master/dist/chiffres-cles.csv")
    data_imported = pd.DataFrame({"country":"France", "granularity":data_raw["granularite"], "name":data_raw["maille_nom"], "confirmed_infected": data_raw["cas_confirmes"], "dead": data_raw["deces"], "recovered": data_raw["reanimation"], "timestamp": data_raw["date"]})
    if data_fr['timestamp'].equals(data_imported['timestamp']):
## if this is true, there are no differences (NO UPDATES)
        print("No updates found")
    else:
        data_fr = data_imported.combine_first(data_fr)
        data_fr.to_csv("France.csv", index = False)
        return(data_fr)

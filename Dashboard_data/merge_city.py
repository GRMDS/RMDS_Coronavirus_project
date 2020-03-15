import pandas as pd
from datetime import datetime
import json


def data_cleaning(df, col_name, last_loaded_date):
    update_date = [x for x in df.columns[4:] if
                   datetime.strptime(x, '%m/%d/%y') > datetime.strptime(last_loaded_date, '%m/%d/%y')]
    df.drop(columns=['Lat','Long'], inplace=True)
    df = df[list(df.columns[:2]) + update_date]
    df['Province/State'].fillna(df['Country/Region'], inplace=True)
    df = df[df['Country/Region'] != 'China']
    table = df.melt(id_vars=df.columns[:2], var_name='updateTime', value_name=col_name)
    return table


def merge_world_city(confirm_df, re_df, death_df):
    df_combine = pd.merge(confirm_df, re_df, on=['Country/Region', 'Province/State', 'updateTime'])
    df_combine = pd.merge(df_combine, death_df, on=['Country/Region', 'Province/State', 'updateTime'])
    # df_combine.drop(columns=['Country/Region_x', 'Country/Region_y'], inplace=True)
    df_combine.rename(columns={"Province/State": "locationEnglishName"}, inplace=True)
    df_combine['updateTime'] = pd.to_datetime(df_combine['updateTime'])
    return df_combine


def reorder_columns(df):
    df['Country/Region'] = 'China'
    df.columns = ['province',
                  'locationName',
                   'locationEnglishName',
                   'confirmedCount',
                   'suspectedCount',
                   'curedCount',
                   'deadCount',
                   'updateTime',
                   'Country/Region',
                   ]
    return df


def separate_province_city(china_df):
    prov_df = china_df[['provinceName',
                        'provinceEnglishName',
                        'province_confirmedCount',
                        'province_suspectedCount',
                        'province_curedCount',
                        'province_deadCount',
                        'updateTime']]
    prov_df.insert(0, 'province', prov_df.provinceEnglishName)
    prov_df = reorder_columns(prov_df)
    prov_df.drop_duplicates(subset=['locationEnglishName', 'updateTime'], keep='first', inplace=True)

    china_df.drop(columns=['provinceName',
                           'province_zipCode',
                           'city_zipCode',
                           'province_suspectedCount',
                           'province_confirmedCount',
                           'province_curedCount',
                           'province_deadCount'], inplace=True)
    china_df = reorder_columns(china_df)
    return prov_df, china_df


def find_new_data(china_df, record):
    last_loc = china_df.loc[
        (china_df['provinceEnglishName'] == record['china_last_province']) &
        (china_df['updateTime'] == record['china_last_record'])
    ].index[0]
    china_df = china_df.iloc[:last_loc, :]
    prov_df, city_df = separate_province_city(china_df)
    china_df_new = pd.concat([prov_df, city_df])
    china_df_new.drop_duplicates(inplace=True)
    return china_df_new


# another method, compare current and historical data
def find_new_from_db(china_df):
    prov_df, city_df = separate_province_city(china_df)
    china_df_loaded = 'data from db'
    china_df_loaded = china_df_loaded[china_df_loaded['Country/Region'] == 'China']
    china_df_new = pd.concat([china_df_loaded, prov_df, city_df]).drop_duplicates(keep=False)
    return  china_df_new


def fetch_data(url, url_re, url_death, url_china):
    df = pd.read_csv(url)
    re_df = pd.read_csv(url_re)
    death_df = pd.read_csv(url_death)

    # temporarily hard coded, should be replaced when have database access
    # last_loaded_time = '3/13/20'

    with open('record.json', 'r') as openfile:
        record = json.load(openfile)
    last_loaded_time = record['last_loaded_time']

    confirm_df = data_cleaning(df, 'confirmedCount', last_loaded_time)
    re_df = data_cleaning(re_df, 'curedCount', last_loaded_time)
    death_df = data_cleaning(death_df, 'deadCount', last_loaded_time)

    df_combine = merge_world_city(confirm_df, re_df, death_df)
    # record = {}
    if not df_combine.empty:
        record['last_loaded_time'] = df_combine.updateTime.max()

    # temporarily hard coded, should be replaced when have database access
    # china_df_loaded = pd.DataFrame()

    china_df = pd.read_csv(url_china)
    china_df.drop_duplicates(inplace=True)

    # use this method to find increment. assuming source data has consistent format and only append new data
    china_df_new = find_new_data(china_df, record)

    if not china_df_new.empty:
        record['china_last_record'] = china_df_new.iloc[0]['updateTime']
        record['china_last_province'] = china_df_new.iloc[0]['province']
    with open("record.json", "w") as outfile:
        json.dump(record, outfile)

    world_df = pd.concat([china_df_new, df_combine])
    if not world_df.empty:
        world_df.to_csv('world_china_merge_' + datetime.now().strftime("%m-%d-%Y-%H-%M-%S") + '.csv',
                        index=False, encoding='utf-8-sig')
    return world_df


url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Confirmed.csv'
url_re = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Recovered.csv'
url_death = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_19-covid-Deaths.csv'
url_china = 'https://raw.githubusercontent.com/BlankerL/DXY-COVID-19-Data/master/csv/DXYArea.csv'

world_df = fetch_data(url, url_re, url_death, url_china)
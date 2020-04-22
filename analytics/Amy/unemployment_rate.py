from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import json
from io import StringIO


def crawl_data(main_url):
	"""
	crawl data from a URL and organize it into a pandas DataFrame
	Input: main_url - a string of url
	Return: pandas DataFrame
	"""

	result = requests.get(main_url)

	# extract data and organize a row as a list
	soup = BeautifulSoup(result.text, 'lxml')
	table = soup.find_all('body')[0]
	data = str(table)
	data = data.split('<body>')[1].split('</body>')[0].split('<p>')[1].split('</p>')[0]
	rows = data.split('\n')

	# split a row so that they could transorm into pandas DataFrame
	output = []
	for r in rows:
		row_ls = r.split("\t")
		for i in range(len(row_ls)):
			row_ls[i] = row_ls[i].strip()
		output.append(row_ls)
	df = pd.DataFrame(output[1:], columns=output[0])

	return df


def split_string(x):
	"""
	split a string with "," and return the second element, if there is no "," in the string, return x
	Input: a string
	Return: a string
	"""
	try:
		return x.split(",")[1].strip()
	except:
		return x


if __name__ == '__main__':
	# dictionary for mapping state names
	us_state = {'AL': 'Alabama',
		 'AK': 'Alaska',
		 'AS': 'American Samoa',
		 'AZ': 'Arizona',
		 'AR': 'Arkansas',
		 'CA': 'California',
		 'CO': 'Colorado',
		 'CT': 'Connecticut',
		 'DE': 'Delaware',
		 'DC': 'District of Columbia',
		 'FL': 'Florida',
		 'GA': 'Georgia',
		 'GU': 'Guam',
		 'HI': 'Hawaii',
		 'ID': 'Idaho',
		 'IL': 'Illinois',
		 'IN': 'Indiana',
		 'IA': 'Iowa',
		 'KS': 'Kansas',
		 'KY': 'Kentucky',
		 'LA': 'Louisiana',
		 'ME': 'Maine',
		 'MD': 'Maryland',
		 'MA': 'Massachusetts',
		 'MI': 'Michigan',
		 'MN': 'Minnesota',
		 'MS': 'Mississippi',
		 'MO': 'Missouri',
		 'MT': 'Montana',
		 'NE': 'Nebraska',
		 'NV': 'Nevada',
		 'NH': 'New Hampshire',
		 'NJ': 'New Jersey',
		 'NM': 'New Mexico',
		 'NY': 'New York',
		 'NC': 'North Carolina',
		 'ND': 'North Dakota',
		 'MP': 'Northern Mariana Islands',
		 'OH': 'Ohio',
		 'OK': 'Oklahoma',
		 'OR': 'Oregon',
		 'PA': 'Pennsylvania',
		 'PR': 'Puerto Rico',
		 'RI': 'Rhode Island',
		 'SC': 'South Carolina',
		 'SD': 'South Dakota',
		 'TN': 'Tennessee',
		 'TX': 'Texas',
		 'UT': 'Utah',
		 'VT': 'Vermont',
		 'VI': 'Virgin Islands',
		 'VA': 'Virginia',
		 'WA': 'Washington',
		 'WV': 'West Virginia',
		 'WI': 'Wisconsin',
		 'WY': 'Wyoming'}


	# collect unemployment rate from 1990 to 2024
	time = ["00-04", "05-09", "10-14", "15-19", "20-24"]
	url_dict = {"00-04": "https://download.bls.gov/pub/time.series/la/la.data.0.CurrentU00-04", 
		"05-09": "https://download.bls.gov/pub/time.series/la/la.data.0.CurrentU05-09",
		"10-14": "https://download.bls.gov/pub/time.series/la/la.data.0.CurrentU10-14",
		"15-19": "https://download.bls.gov/pub/time.series/la/la.data.0.CurrentU15-19",
		"20-24": "https://download.bls.gov/pub/time.series/la/la.data.0.CurrentU20-24",
		"area": "https://download.bls.gov/pub/time.series/la/la.area"}

	# for each URL, crawl to a pandas dataframe and save the dataframe in a dictionary
	df_dict = {}
	for url in url_dict:
		df = crawl_data(url_dict[url])
		df_dict[url] = df
	
	# append employment data from 1990 to 2024 into one single big dataframe
	all_data = pd.DataFrame()
	for t in time:
		all_data = all_data.append(df_dict[t], ignore_index=True)

	# extract area_code and measure_code from series_id
	all_data["area_code"] = all_data["series_id"].apply(lambda x: x[3:-2])
	all_data["measure_code"] = all_data["series_id"].apply(lambda x: x[-2:])
	#print(all_data.isnull().sum())
	all_data["period"] = all_data["period"].fillna("")
	all_data["month"] = all_data["period"].apply(lambda x: x.strip("M"))
	
	# filter records that are unemployment rate measures (measure_code == "03")
	all_data = all_data.loc[all_data["measure_code"] == "03", :]

	# extract county level area_code from area_df ("area_type_code" == "F")
	area_df = df_dict["area"]
	county_df = area_df.loc[area_df["area_type_code"] == "F", :]
	
	# match county names to all_data using county_df
	all_data = all_data.merge(county_df[["area_code", "area_text"]], on="area_code", how="left").fillna(0)
	all_data = all_data.loc[(all_data["area_text"] != 0)&(all_data["month"] != "13")&(all_data["month"] != ""), ["year", "month", "value", "area_text"]]
	# change the format to match data in MongoDB
	all_data["date"] = pd.to_datetime(all_data["year"] + all_data["month"], format="%Y%m")
	all_data = all_data[["area_text", "date", "value"]].sort_values(["area_text", "date"]).rename(columns={"value": "unemployment_rate"})
	# create a dataframe "county_level" that represents one county as a row
	county_level = all_data["area_text"].value_counts().reset_index().rename(columns={"index": "area_text", "area_text": "count"})
	tmp = all_data.groupby("area_text")["date"].first().reset_index().rename(columns={"date": "StartDate"})
	county_level = county_level.merge(tmp, on="area_text")
	tmp = all_data.groupby("area_text")["date"].last().reset_index().rename(columns={"date": "EndDate"})
	county_level = county_level.merge(tmp, on="area_text")
	# put all unemployment rates of a county into a list
	tmp = all_data.groupby("area_text")["unemployment_rate"].agg(lambda x: x.values.tolist()).reset_index()
	county_level = county_level.merge(tmp, on="area_text")
	#county_level["unemployment_rate"] = np.asarray(county_level["unemployment_rate"])
	#county_level["check"] = ((county_level["EndDate"]-county_level["StartDate"]) / np.timedelta64(1, 'M')).astype(int)

	# split area_text into state and county
	county_level["state"] = county_level["area_text"].apply(lambda x: split_string(x)).map(us_state)
	county_level["state"] = county_level["state"].fillna(county_level["area_text"])
	county_level["county"] = county_level["area_text"].apply(lambda x: x.split(",")[0].strip())
	# select only the columns needed and transform them into json 
	county_level = county_level[["county", "state", "StartDate", "EndDate", "unemployment_rate"]]
	county_level["StartDate"] = county_level["StartDate"].dt.strftime('%Y-%m-%d')
	county_level["EndDate"] = county_level["EndDate"].dt.strftime('%Y-%m-%d')
	s = StringIO(county_level.to_json(orient='records'))
	print(json.load(s))



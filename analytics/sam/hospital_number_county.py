# source: https://data.medicare.gov/Hospital-Compare/Hospital-General-Information/xubh-q36u

import pandas as pd
from sodapy import Socrata

BASE_URL = "data.medicare.gov"
PATH = 'xubh-q36u'

us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands': 'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}
abbrev_us_state = dict(map(reversed, us_state_abbrev.items()))


def hospital_num_county():
    client = Socrata(BASE_URL, None)
    results = client.get(PATH, limit=10000)
    hospital = pd.DataFrame.from_records(results)
    hospital = hospital[['hospital_name', 'state', 'county_name']]
    hospital_count = hospital.groupby(['state', 'county_name']).size().rename('count').reset_index()
    hospital_count['state'] = hospital_count['state'].map(abbrev_us_state)
    hospital_count['county_name'] = hospital_count['county_name'].str.lower().str.title()
    hospital_count['county_name'] = hospital_count['county_name'].astype(str) + ' County'
    hospital_count_json = hospital_count.to_json(orient='records')

    print(hospital_count_json)



if __name__ == '__main__':
    hospital_num_county()
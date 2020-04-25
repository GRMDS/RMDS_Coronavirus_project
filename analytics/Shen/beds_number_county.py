# The purpose of this notebook is as follows :
# 1. Create a function to retrice number of beds at county level
# 
# 2. Create a function to clean collected data
#
# 3. Create a function to combine previous two functions and output data in appopriate format for MongoDB inserting



### I can only fetch 2000 record at a time from HIFLD's API so I split them into 4 segments.
url_0_2000 = 'https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/Hospitals_1/FeatureServer/0/query?where=OBJECTID%20%3E%3D%200%20AND%20OBJECTID%20%3C%3D%202000&outFields=OBJECTID,CITY,STATE,ZIP,COUNTY,COUNTRY,BEDS&returnGeometry=false&outSR=4326&f=json'
url_2001_4000 = 'https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/Hospitals_1/FeatureServer/0/query?where=OBJECTID%20%3E%3D%202001%20AND%20OBJECTID%20%3C%3D%204000&outFields=OBJECTID,CITY,STATE,ZIP,COUNTY,COUNTRY,BEDS&returnGeometry=false&outSR=4326&f=json'
url_4001_6000 = 'https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/Hospitals_1/FeatureServer/0/query?where=OBJECTID%20%3E%3D%204001%20AND%20OBJECTID%20%3C%3D%206000&outFields=OBJECTID,CITY,STATE,ZIP,COUNTY,COUNTRY,BEDS&returnGeometry=false&outSR=4326&f=json'
url_6001_7581 = 'https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/Hospitals_1/FeatureServer/0/query?where=OBJECTID%20%3E%3D%206001%20AND%20OBJECTID%20%3C%3D%208000&outFields=OBJECTID,CITY,STATE,ZIP,COUNTY,COUNTRY,BEDS&returnGeometry=false&outSR=4326&f=json'
url_list = [url_0_2000,url_2001_4000, url_4001_6000, url_6001_7581]



url = url_list
ATTRIBUTES = ['state_name', 'country_name', 'num_beds']
GRANULARITY = 'county'

def retrive_from_API(url):
    '''
    This function takes the url of HIFLD API and reformat it into a dataframe
    Input: URL
    Output: Datafarme
    
    '''
    beds_list = []
    if len(list(url))>=1:
        for i in list(url):
            response = requests.get(url=i)
            list_1 = [i['attributes'] for i in response.json()['features']]
            beds_list += list_1
    else:
        response = requests.get(url)
        beds_list = [i['attributes'] for i in response.json()['features']]
    
    beds_df = pd.DataFrame.from_dict(beds_list)
    return beds_df


def cleaning(df):
    '''
    Input: dataframe
    - chagne state abbreviation to its full name
    - remove records that do not have county attached
    - fill in missing value with 0
    Output: cleaned dataframe

    '''
    beds_df = df
    beds_df.drop(columns = ['COUNTRY', 'ZIP', 'OBJECTID', 'CITY'], inplace = True)
    beds_df = beds_df[beds_df.COUNTY!='NOT AVAILABLE COUNTY']
    beds_df = beds_df[beds_df.COUNTY!='NOT AVAILABLE']
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
    'Northern Mariana Islands':'MP',
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
    beds_df.STATE = [abbrev_us_state[val] for val in beds_df.STATE ]
    beds_df.COUNTY = [val + ' COUNTY' for val in beds_df.COUNTY]
    beds_df.BEDS = [0 if x<0 else x for x in beds_df.BEDS]
    beds_df.columns = ['state_name', 'county_name','num_beds']
    beds_df = beds_df.groupby(['state_name','county_name']).sum().reset_index()
    return beds_df

def bed_num_county():
    '''
    This function takes url of HIFLD API
    Call retrive_from_API and cleaning two functions
    Convert dataframe to list of dictionaries 
    '''
    import pandas as pd
    import requests
    df_1 = retrive_from_API(url)
    df_2 = cleaning(df_1)
    beds_dict = df_2.to_dict('record')
    return beds_dict

if __name__ == '__main__':
    x = bed_num_county()
    
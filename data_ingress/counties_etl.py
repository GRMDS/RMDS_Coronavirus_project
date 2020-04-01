import argparse
from collections import defaultdict
import csv
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pymongo import MongoClient
import requests
from typing import Dict, List
import us


BASE_URL = 'https://api.census.gov'
PATH = 'data/2019/pep/population'
ATTRIBUTES = ['date_desc', 'pop', 'name']
GRANULARITY = 'county'


class ZipcodeType(Enum):

    """Zipcode types."""

    STANDARD = 'STANDARD'
    PO_BOX = 'PO BOX'
    UNIQUE = 'UNIQUE'
    MILITARY = 'MILITARY'


@dataclass
class County:

    """Represents an entity with county data."""

    date_collected: datetime
    population: int
    county_name: str
    state_name: str
    zipcodes: List[str]

    @classmethod
    def from_census(cls, zipcode_data: Dict[str, List[str]], date_desc: str, pop: str, name: str):
        """Parses an entity from the census API."""
        date_collected = datetime.strptime(date_desc.split(' ')[0], '%m/%d/%Y')
        population = int(pop)
        county_name, state_name = name.split(', ')

        state_abbr = us.states.lookup(state_name).abbr
        zipcodes = zipcode_data[(county_name, state_abbr)]

        return cls(date_collected, population, county_name, state_name, zipcodes)


def get_county_data(
    zipcodes_csv: str,
    include_po_box_zips: bool,
    mongodb_host: str,
    mongodb_port: int,
    mongodb_dest_database: str,
    mongodb_dest_collection: str,
    mongodb_username: str,
    mongodb_password: str,
):
    zipcode_data = get_county_zipcodes(zipcodes_csv, include_po_box_zips)

    params = {
        'get': ','.join([attr.upper() for attr in ATTRIBUTES]),
        'for': f'{GRANULARITY}:*',
    }
    response = requests.get(url=f'{BASE_URL}/{PATH}', params=params)

    county_data = response.json()

    # The first row is just field names
    county_data = county_data[1:]

    # Truncate each item to just the fields we asked for since the response contains extra
    county_data = [county[:len(ATTRIBUTES)] for county in county_data]

    # Instantiate each county in structured form
    counties = [County.from_census(zipcode_data, *county) for county in county_data]

    # Insert each county into the database
    insert_counties_into_db(
        counties,
        mongodb_host,
        mongodb_port,
        mongodb_dest_database,
        mongodb_dest_collection,
        mongodb_username,
        mongodb_password,
    )


def get_county_zipcodes(zipcodes_csv: str, include_po_box_zips: bool):
    with open(zipcodes_csv, 'r') as zipcodes_csv_file:
        zipcodes = csv.DictReader(zipcodes_csv_file)

        zipcodes_by_county = defaultdict(list)

        for zipcode in zipcodes:
            zipcode_type = ZipcodeType(zipcode['type'])

            if zipcode_type != ZipcodeType.PO_BOX or include_po_box_zips:
                zipcodes_by_county[(zipcode['county'], zipcode['state'])].append(zipcode['zip'])

        return zipcodes_by_county


def insert_counties_into_db(
    counties: List[County],
    mongodb_host: str,
    mongodb_port: int,
    mongodb_dest_database: str,
    mongodb_dest_collection: str,
    mongodb_username: str,
    mongodb_password: str,
):
    if mongodb_username and mongodb_password:
        mongo_client = MongoClient(
            mongodb_host,
            mongodb_port,
            username=mongodb_username,
            password=mongodb_password,
            authSource=mongodb_dest_database,
            authMechanism='SCRAM-SHA-256',
        )
    else:
        mongo_client = MongoClient(mongodb_host, mongodb_port)

    db = mongo_client[mongodb_dest_database]
    collection = db[mongodb_dest_collection]

    # We are replacing the entire dataset each time this script is run
    collection.drop()

    collection.insert_many([asdict(county) for county in counties])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pulls US census data to find population distribution by counties')

    parser.add_argument('--zipcodes_csv', help='The file containing US zipcodes (https://www.unitedstateszipcodes.org/zip-code-database/)')
    parser.add_argument('--include_po_box_zips', help='Whether to include PO BOX zipcodes', type=bool, default=True)
    parser.add_argument('--mongodb_host', help='The hostname of the mongodb server', default='localhost')
    parser.add_argument('--mongodb_port', help='The port to connect through for the mongodb server', type=int, default=27017)
    parser.add_argument('--mongodb_dest_database', help='The database to store the county demographics data in', default='COVID19-DB')
    parser.add_argument('--mongodb_dest_collection', help='The collection to store the county demographics data in', default='counties')
    parser.add_argument('--mongodb_username', help='The username of the mongodb instance', default=None)
    parser.add_argument('--mongodb_password', help='The password of the mongodb instance', default=None)

    get_county_data(**vars(parser.parse_args()))

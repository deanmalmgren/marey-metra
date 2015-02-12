"""This module is used to parse data from GTFS (google transit data) and put the
result in the same format as what metra expects for the rail time tracker api.
"""
import re
import os
import csv

from django.conf import settings

from utils import strip


def get_route(trip_id):
    """get the route name from the trip_id"""
    return trip_id.split('_')[0]


def get_train_number(trip_id):
    """Get the train number that is associated with this trip_id"""
    x = trip_id.split('_')[1]
    match = re.match(r'[a-zA-Z ]+(?P<train_number>\d+)', x)
    return int(match.groupdict()['train_number'])


def get_version(trip_id):
    """get the version string from the trip_id"""
    return trip_id.split('_')[2]


def get_train_info(trip_id):
    return get_route(trip_id), get_train_number(trip_id), get_version(trip_id)

def get_stations(trip_id):
    """get all of the stations that are associated with this trip_id"""

    # read in the stop times to find all of the trips. this information
    # needs to be passed along to the
    filename = os.path.join(settings.GTFS_DIR, 'stop_times.txt')
    stations = []
    with CsvReader(filename) as reader:
        for row in reader:
            if row['trip_id'] == trip_id:
                stations.append(row['stop_id'])
    return stations


class CsvReader(object):
    """this class is used to read the funky CSVs that are included in the GTFS
    data and standardize the output"""

    def __init__(self, filename):
        self.filename = filename
        self.stream = None
        self.reader = None

    def __enter__(self):
        self.stream = open(self.filename, 'r')
        self.reader = csv.DictReader(self.stream)
        return self

    def __exit__(self, type, value, traceback):
        self.stream.close()

    def __iter__(self):
        for row in self.reader:
            yield strip(row)

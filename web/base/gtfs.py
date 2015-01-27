"""This module is used to parse data from GTFS (google transit data) and put the
result in the same format as what metra expects for the rail time tracker api.
"""
import re
import os
import csv

from django.conf import settings

from utils import strip

# probably this shouldn't be hard coded and it should be passed in by flo.yaml,
# but this is a good way to get started
GTFS_DIR = os.path.join(settings.PROJECT_ROOT, '..', 'data', 'metra_gtfs')

def get_train_number(trip_id):
    """Get the train number that is associated with this trip_id"""
    x = trip_id.split('_')[1]
    match = re.match(r'[a-zA-Z]+(?P<train_number>\d+)', x)
    return int(match.groupdict()['train_number'])


def get_route(trip_id):
    """get the route name from the trip_id"""
    return trip_id.split('_')[0]


def get_stations(trip_id, gtfs_dir=GTFS_DIR):
    """get all of the stations that are associated with this trip_id"""

    # read in the stop times to find all of the trips. this information
    # needs to be passed along to the
    stations = []
    with open(os.path.join(gtfs_dir, 'stop_times.txt')) as stream:
        reader = csv.DictReader(stream)
        for row in map(strip, reader):
            if row['trip_id'] == trip_id:
                stations.append(row['stop_id'])
    return stations

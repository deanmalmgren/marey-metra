#!/usr/bin/env python

"""parse the stop_times.txt CSV from the downloaded GTFS data from Metra

https://developers.google.com/transit/gtfs/reference?hl=fr-FR#stop_times_fields
"""

import sys
import os
import csv
import collections
import re

from utils import strip

gtfs_dir = sys.argv[1]

def is_one(value):
    return 1 == int(value)

# read in the schedules
services = {}
with open(os.path.join(gtfs_dir, 'calendar.txt')) as stream:
    reader = csv.DictReader(stream)
    for row in map(strip, reader):
        services[row['service_id']] = []
        for abbr in ['sun', 'mon', 'tues', 'wednes', 'thurs', 'fri', 'satur']:
            day = abbr + 'day'
            services[row['service_id']].append(is_one(row[day]))

# read in the trips dictionary
trip_services = {}
with open(os.path.join(gtfs_dir, 'trips.txt')) as stream:
    reader = csv.DictReader(stream)
    for row in map(strip, reader):
        trip_services[row['trip_id']] = row['service_id']

# find the start time of the route from the stop times
trips = collections.defaultdict(list)
with open(os.path.join(gtfs_dir, 'stop_times.txt')) as stream:
    reader = csv.DictReader(stream)
    for row in map(strip, reader):
        trips[row['trip_id']].append((
            int(row['stop_sequence']),
            row['stop_id'],
            row['departure_time'],
        ))

# print out the crontab
script_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'query_rail_time_tracker.py',
)
for trip_id, service_id in trip_services.iteritems():
    trips[trip_id].sort()

    # get the hours and minutes
    first_stop = trips[trip_id][0][-1]
    hours, minutes, secondes = first_stop.split(':')
    day_indices = [i for i, yes in enumerate(services[service_id]) if yes]
    days = ','.join(map(str, day_indices))
    command = "python %s %s" % (script_path, trip_id)


    print minutes, hours, '*', '*', days, '*', command


#     print >> sys.stderr, first_stop, trip_id, service_id
#     fuck

# print >> sys.stderr, trip_services

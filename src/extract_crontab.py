#!/usr/bin/env python

"""parse the stop_times.txt CSV from the downloaded GTFS data from Metra

https://developers.google.com/transit/gtfs/reference?hl=fr-FR#stop_times_fields
"""

import sys
import os
import csv
import collections
import re

gtfs_dir = sys.argv[1]

def is_one(value):
    return 1 == int(value)

# this was copied over from www.base.utils could alternatively create a soft
# link to the utils.py file to make this a little easier and not have to muck
# with python paths
def strip(row):
    """strip all extra space off of native python objects"""
    if isinstance(row, dict):
        return dict((k.strip(), v.strip()) for k, v in row.iteritems())
    elif isinstance(row, list):
        return [x.strip() for x in row]
    else:
        raise TypeError

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
print "MAILTO=dean.malmgren@datascopeanalytics.com"
print "PATH=/usr/sbin:/usr/bin:/sbin:/bin"
print ""
www_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'www',
)
for trip_id, service_id in trip_services.iteritems():
    trips[trip_id].sort()

    # get the hours and minutes
    first_stop = trips[trip_id][0][-1]
    hours, minutes, secondes = first_stop.split(':')
    day_indices = [i for i, yes in enumerate(services[service_id]) if yes]
    days = ','.join(map(str, day_indices))
    command = (
        "cd %s && "
        "./manage.py query_rail_time_tracker %s > /dev/null"
    ) % (www_path, trip_id)

    if "UP-W" in trip_id:
        print minutes, hours, '*', '*', days, command

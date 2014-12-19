#!/usr/bin/env python

"""This script polls the Rail Time Tracker
(https://metrarail.com/metra/wap/en/home/RailTimeTracker.html) to
determine what the current status is on a given route in the Metra
system. You should start running this script ~5 minutes before the
train is due to arrive in the station.

pass a trip_id to this script, which then looks up the schedule for
this particular trip and monitors its timeliness.

This script is intended to be run by cron.
"""

import sys
import argparse
import json

import requests

from utils import strip, js2pydate

# trip_id = sys.argv[1]
# gtfs_dir = sys.argv[1]

# # TODO: this can be moved into the actual scraper. the scraper can
# # read in the schedule when it first launches based on the trip_id
#
# # read in the stop times to find all of the trips. this information
# # needs to be passed along to the
# trips = collections.defaultdict(list)
# with open(os.path.join(gtfs_dir, 'stop_times.txt')) as stream:
#     reader = csv.DictReader(stream)
#     for row in map(strip, reader):
#         trips[row['trip_id']].append((
#             row['stop_sequence'],
#             row['stop_id'],
#             row['departure_time'],
#         ))
#
# # have this script end prematurely
# print >> sys.stderr, "NOT DONE YET"
# sys.exit(0)
# fuck

stations = (
    "ELBURN",
    "LAFOX",
    "GENEVA",
    "WCHICAGO",
    "WINFIELD",
    "WHEATON",
    "COLLEGEAVE",
    "GLENELLYN",
    "LOMBARD",
    "VILLAPARK",
    "ELMHURST",
    "BERKELEY",
    "BELLWOOD",
    "MELROSEPK",
    "MAYWOOD",
    "RIVRFOREST",
    "OAKPARK",
    "KEDZIE",
    "OTC",
)

# post a request to the API
post_data = {"stationRequest": {
    "Corridor": "UP-W",
    "Destination": "OTC",
    "Origin": stations[2],
}}
headers = {'content-type': 'application/json'}
response = requests.post(
    "http://12.205.200.243/AJAXTrainTracker.svc/GetAcquityTrainData",
    # "http://75.144.111.115/AJAXTrainTracker.svc/GetAcquityTrainData", #backup?
    data=json.dumps(post_data),
    headers=headers,
)

# extract the estimated departure time for this post.
if response.status_code == 200:
    result = json.loads(response.text)
    data = json.loads(result['d'])
    train1 = data['train1']
    print train1['train_num'], js2pydate(train1['estimated_dpt_time']), js2pydate(train1['scheduled_dpt_time']),

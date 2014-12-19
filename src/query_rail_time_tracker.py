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
import datetime
import time

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
route = "UP-W"
train_number = 38


class MockResponse(object):
    status_code = None

def query_rail_time_tracker(route, train_number, origin, destination):

    # prepare the post data to the API
    post_data = {"stationRequest": {
        "Corridor": route,
        "Origin": origin,
        "Destination": destination,
    }}

    # make requests until we get an 'OK' response
    response = MockResponse()
    while response.status_code != 200:
        response = requests.post(
            "http://12.205.200.243/AJAXTrainTracker.svc/GetAcquityTrainData",
            # "http://75.144.111.115/AJAXTrainTracker.svc/GetAcquityTrainData", #backup?
            data=json.dumps(post_data),
            headers={'content-type': 'application/json'},
        )

    # extract the estimated departure time for this train
    result = json.loads(response.text)
    data = json.loads(result['d'])
    estimated_departure_time = None
    for i in range(1,4):
        train = data['train%d' % i]
        if int(train['train_num']) == train_number:
            estimated_departure_time = js2pydate(train['estimated_dpt_time'])
            break

    return estimated_departure_time

# for each station, query the rail time tracker API until we have the last
# possible 'estimated departure time', which corresponds with the actual
# departure time
estimated_departure_times = dict.fromkeys(stations, None)
is_done = dict.fromkeys(stations, False)
while not all(is_done.values()):

    # for each station along this route, query the rail time tracker API
    for origin_station in stations:
        if not is_done[origin_station]:
            t = query_rail_time_tracker(
                route, train_number, origin_station, stations[-1],
            )
            if isinstance(t, datetime.datetime):
                estimated_departure_times[origin_station] = t
            else:
                is_done[origin_station] = True

    # pause for a bit before making another round of requests
    for station in stations:
        print station, is_done[station], estimated_departure_times[station]
    print ''
    time.sleep(30)

# TODO save everything to a database or something

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
import gtfs

# get the trip id command line argument
trip_id = sys.argv[1]

# use the trip id to get a bunch of other information from gtfs
route = gtfs.get_route(trip_id)
train_number = gtfs.get_train_number(trip_id)
stations = gtfs.get_stations(trip_id)


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
    estimated_departure_time, scheduled_departure_time = None, None
    for i in range(1,4):
        train = data['train%d' % i]
        if int(train['train_num']) == train_number:
            estimated_departure_time = js2pydate(train['estimated_dpt_time'])
            scheduled_departure_time = js2pydate(train['scheduled_dpt_time'])
            break

    return estimated_departure_time, scheduled_departure_time

# for each station, query the rail time tracker API until we have the last
# possible 'estimated departure time', which corresponds with the actual
# departure time
estimated_departure_times = dict.fromkeys(stations, None)
scheduled_departure_times = dict.fromkeys(stations, None)
is_done = dict.fromkeys(stations, False)
while not all(is_done.values()):

    # for each station along this route, query the rail time tracker API
    for origin_station in stations:
        if not is_done[origin_station]:
            t_estimated, t_scheduled = query_rail_time_tracker(
                route, train_number, origin_station, stations[-1],
            )
            if isinstance(t_estimated, datetime.datetime):
                estimated_departure_times[origin_station] = t_estimated
                scheduled_departure_times[origin_station] = t_scheduled
            else:
                is_done[origin_station] = True

    # pause for a bit before making another round of requests
    for station in stations:
        print station, is_done[station], estimated_departure_times[station],\
            scheduled_departure_times[station]
    print ''
    time.sleep(30)

# TODO save everything to a database or something

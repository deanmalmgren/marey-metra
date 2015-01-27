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
import json
import datetime
import time
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
import requests

import base.gtfs as gtfs


class MockResponse(object):
    status_code = None


class Command(BaseCommand):
    args = '<trip_id>'
    help = "query the rail time tracker to record a train's progress"
    option_list = BaseCommand.option_list + (
        make_option('-s', '--sleep-time',
            action='store',
            type='int',
            dest='sleep_time',
            default=30,
            help=(
                'amount of time to sleep between Rail Time Tracker pings. '
                '[default: %default seconds]'
            )),
        )

    # fix the user agent string for faster response times
    # http://www.useragentstring.com/
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
    }

    def handle(self, *args, **kwargs):

        # get the trip id command line argument
        trip_id = args[0]
        sleep_time = kwargs['sleep_time']

        # use the trip id to get a bunch of other information from gtfs
        route = gtfs.get_route(trip_id)
        train_number = gtfs.get_train_number(trip_id)
        stations = gtfs.get_stations(trip_id)

        # for each station, query the rail time tracker API until we have the last
        # possible 'tracked departure time', which corresponds with the actual
        # departure time
        tracked_departure_times = dict.fromkeys(stations, None)
        scheduled_departure_times = dict.fromkeys(stations, None)
        is_done = dict.fromkeys(stations, False)
        while not all(is_done.values()):

            # for each station along this route, query the rail time tracker API
            for origin_station in stations[:-1]:
                if not is_done[origin_station]:
                    a, b, c, d = self.query_rail_time_tracker(
                        route, train_number, origin_station, stations[-1],
                    )
                    if isinstance(a, datetime.datetime):
                        tracked_departure_times[origin_station] = a
                        scheduled_departure_times[origin_station] = b
                        tracked_departure_times[stations[-1]] = c
                        scheduled_departure_times[stations[-1]] = d
                    else:
                        is_done[origin_station] = True
                        is_done[stations[-1]] = True

            # pause for a bit before making another round of requests
            for station in stations:
                print station, is_done[station], tracked_departure_times[station],\
                    scheduled_departure_times[station]
            print ''
            time.sleep(sleep_time)

        # TODO save everything to a database or something

    def query_rail_time_tracker(self, route, train_number, origin, destination):
        # prepare the post data to the API
        request_data = {
            "line": route,
            "origin": origin,
            "destination": destination,
        }

        # make requests until we get an 'OK' response
        response = MockResponse()
        while response.status_code != 200:
            response = requests.get(
                "http://metrarail.com/content/metra/en/home/jcr:content/trainTracker.get_train_data.json",
                params=request_data,
                headers=self.headers
            )
        result = json.loads(response.text)

        # extract the tracked departure time for this train
        tracked_departure_time, scheduled_departure_time = None, None
        tracked_arrival_time, scheduled_arrival_time = None, None
        for i in range(1,3):
            print result.keys()
            train = result['train%d' % i]
            if int(train['train_num']) == train_number:
                if train['hasData']:
                    tracked_departure_time = train['estimated_dpt_time']
                    scheduled_departure_time = train['scheduled_dpt_time']
                    tracked_arrival_time = train['estimated_arv_time']
                    scheduled_arrival_time = train['scheduled_arv_time']
                else:
                    tracked_departure_time = scheduled_departure_time = train['scheduled_dpt_time']
                    tracked_arrival_time = scheduled_arrival_time = train['scheduled_arv_time']
                tracked_departure_time = self.cast_as_time(tracked_departure_time)
                scheduled_departure_time = self.cast_as_time(scheduled_departure_time)
                tracked_arrival_time = self.cast_as_time(tracked_arrival_time)
                scheduled_arrival_time = self.cast_as_time(scheduled_arrival_time)
                break

        return (
            tracked_departure_time, scheduled_departure_time,
            tracked_arrival_time, scheduled_arrival_time,
        )

    def cast_as_time(self, time_as_string):
        t = datetime.datetime.strptime(time_as_string, "%H:%M")
        today = datetime.date.today()
        return t.replace(today.year, today.month, today.day)

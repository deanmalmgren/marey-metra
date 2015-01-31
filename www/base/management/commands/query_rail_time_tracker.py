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
from base.models import Punchcard


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
        self.trip_id = trip_id = args[0]
        sleep_time = kwargs['sleep_time']

        # use the trip id to get a bunch of other information from gtfs
        route = gtfs.get_route(trip_id)
        train_number = gtfs.get_train_number(trip_id)
        stations = gtfs.get_stations(trip_id)

        # for each station, query the rail time tracker API until we have the last
        # possible 'tracked departure time', which corresponds with the actual
        # departure time
        tracked_times = dict.fromkeys(stations, None)
        scheduled_times = dict.fromkeys(stations, None)
        is_done = dict.fromkeys(stations, False)
        while not all(is_done.values()):

            # for each station along this route, query the rail time tracker API
            for origin_station in stations[:-1]:
                if not is_done[origin_station]:
                    try:
                        a, b, c, d = self.query_rail_time_tracker(
                            route, train_number, origin_station, stations[-1],
                        )
                    except Exception, e:
                        sys.stderr.write(self.get_error_message(
                            origin_station, stations[-1],
                        ))
                        sys.stderr.write('\n\n' + '-'*80 + '\n\n')
                        raise e
                    if isinstance(a, datetime.datetime):
                        tracked_times[origin_station] = a
                        scheduled_times[origin_station] = b
                        tracked_times[stations[-1]] = c
                        scheduled_times[stations[-1]] = d
                    else:
                        is_done[origin_station] = True
                        is_done[stations[-1]] = True

            # pause for a bit before making another round of requests
            self.update_progress(stations, is_done, tracked_times, scheduled_times)
            time.sleep(sleep_time)

        # save everything to a database or something
        for station in stations:
            punchcard = Punchcard(
                trip_id=trip_id,
                distance_traveled=0,
                stop_id=station,
                scheduled_time=scheduled_times[station],
                tracked_time=tracked_times[station],
            )
            punchcard.save()
        print "...done"

    def update_progress(self, stations, is_done, tracked_times, scheduled_times):
        for station in stations:
            print station, is_done[station], tracked_times[station],\
                scheduled_times[station]
        print ''

    def get_error_message(self, origin, destination):
        trip_id = self.trip_id
        return (
            'Exception raised when querying the rail time tracker for trip '
            '%(trip_id)s traveling from %(origin)s to %(destination)s. \n\n'
        ) % locals() + (
            'Response back from server: \n\n%s\n\n'
        ) % json.dumps(json.loads(self.response.text), indent=2, sort_keys=True)


    def query_rail_time_tracker(self, route, train_number, origin, destination):
        # prepare the post data to the API
        request_data = {
            "line": route,
            "origin": origin,
            "destination": destination,
        }

        # make requests until we get an 'OK' response
        self.response = MockResponse()
        while self.response.status_code != 200:
            self.response = requests.get(
                "http://metrarail.com/content/metra/en/home/jcr:content/trainTracker.get_train_data.json",
                params=request_data,
                headers=self.headers
            )
        result = json.loads(self.response.text)

        # extract the tracked departure time for this train
        tracked_departure_time, scheduled_departure_time = None, None
        tracked_arrival_time, scheduled_arrival_time = None, None
        is_train = lambda key: key.startswith('train')
        for key in filter(is_train, result.keys()):
            train = result[key]
            if int(train['train_num']) == train_number:
                scheduled_departure_time = train['scheduled_dpt_time'] + train['schDepartInTheAM']
                scheduled_arrival_time = train['scheduled_arv_time'] + train['schArriveInTheAM']
                if train['hasData']:
                    tracked_departure_time = train['estimated_dpt_time'] + train['estDepartInTheAM']
                    tracked_arrival_time = train['estimated_arv_time'] + train['estArriveInTheAM']
                else:
                    tracked_departure_time = scheduled_departure_time
                    tracked_arrival_time = scheduled_arrival_time
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
        t = datetime.datetime.strptime(time_as_string, "%I:%M%p")
        today = datetime.date.today()
        return t.replace(today.year, today.month, today.day)

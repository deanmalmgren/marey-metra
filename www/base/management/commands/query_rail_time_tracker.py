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
            dest='min_sleep_time',
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

    # use this to tune how frequently this scripts hits the rail time tracker
    # API
    n_stations = 3

    def handle(self, *args, **kwargs):

        # get the trip id command line argument
        self.trip_id = trip_id = args[0]
        min_sleep_time = kwargs['min_sleep_time']

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

            # for each station along this route, query the rail time tracker
            # API. The We try to do this as nicely as possible for the API, so
            # we only query the next n_stations stations that aren't done.
            n = 0
            next_station = None
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

                    # only look at the next n_stations that aren't yet done to
                    # be as friendly as possible to the API
                    next_station = next_station or origin_station
                    n += 1
                    if n >= self.n_stations:
                        break

            # update progress to stdout
            self.update_progress(
                stations, is_done, tracked_times, scheduled_times
            )

            # pause for a bit before making another round of requests. to be as
            # friendly to the API as possible, this tunes the time to be the
            # maximum of the specified min_sleep_time or half of the time to the
            # next train's estimated arrival
            now = datetime.datetime.now()
            next_time = tracked_times[next_station]
            if next_time < now:
                sleep_time = min_sleep_time
            else:
                dt = tracked_times[next_station] - datetime.datetime.now()
                sleep_time = max(min_sleep_time, dt.seconds/2)
            self.countdown(sleep_time, next_station)

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

    def countdown(self, sleep_time, next_station):
        for i in range(sleep_time, 0, -1):
            sys.stdout.write((
                "Next stop %(next_station)s. "
                "Repinging API in %(i)3d seconds...\r"
            ) % locals())
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write('\n')

    def update_progress(self, stations, is_done, tracked_times, scheduled_times):
        for station in stations:
            done = ' '
            if is_done[station]:
                done = u"\u2713"
            if None in (tracked_times[station], scheduled_times[station]):
                dt = ""
            else:
                dt = tracked_times[station] - scheduled_times[station]
                dt = dt.seconds/60
                if dt>0:
                    dt = "+" + str(dt) + " late"
                else:
                    dt = str(dt) + " early"
            s = "%s %20s %21s %21s  %s" % (
                done, station, tracked_times[station],
                scheduled_times[station], dt
            )
            print s.encode('utf-8')
        print ''

    def get_error_message(self, origin, destination):
        trip_id = self.trip_id
        msg = (
            'Exception raised when querying the rail time tracker for trip '
            '%(trip_id)s traveling from %(origin)s to %(destination)s. \n\n'
        ) % locals()
        msg += (
            'Response (%s) back from server: '
        ) % (self.response.status_code, )
        try:
            msg += '\n\n%s\n\n' % (
                 json.dumps(json.loads(self.response.text), indent=2, sort_keys=True)
            )
        except:
            pass
        return msg

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

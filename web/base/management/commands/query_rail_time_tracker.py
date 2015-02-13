import sys
import json
import datetime
import time
import StringIO
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
import requests

import base.gtfs as gtfs
from base.models import Route, Station, Punchcard


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

        # remember what time we started for debugging purposes
        self.started_script = datetime.datetime.now()

        # get the trip id command line argument
        self.trip_id = args[0]
        self.min_sleep_time = kwargs['min_sleep_time']

        # use the trip id to get a bunch of other information from gtfs
        self.route = gtfs.get_route(self.trip_id)
        self.train_number = gtfs.get_train_number(self.trip_id)
        self.stations = gtfs.get_stations(self.trip_id)

        # for each station, query the rail time tracker API until we have the last
        # possible 'tracked departure time', which corresponds with the actual
        # departure time
        self.tracked_times = dict.fromkeys(self.stations, None)
        self.scheduled_times = dict.fromkeys(self.stations, None)
        self.is_done = dict.fromkeys(self.stations, False)
        while not all(self.is_done.values()):
            self.query_all_trains()
            self.update_progress()
            self.pause()
            break

        # save everything to a database or something
        self.save_punchcards()
        print "...done"

    def query_all_trains(self):
        """for each station along this route, query the rail time tracker
        API. The We try to do this as nicely as possible for the API, so
        we only query the next n_stations stations that aren't done.
        """
        n = 0
        is_first_time = len(set(self.scheduled_times.values())) == 1
        self.next_station = None
        for origin_station in self.stations[:-1]:
            if not self.is_done[origin_station]:
                try:
                    a, b, c, d = self.query_rail_time_tracker(
                        origin_station,
                    )
                except Exception, e:
                    sys.stderr.write(self.get_error_message(origin_station))
                    sys.stderr.write('\n\n' + '-'*80 + '\n\n')
                    raise e
                if isinstance(a, datetime.datetime):
                    self.tracked_times[origin_station] = a
                    self.scheduled_times[origin_station] = b
                    self.tracked_times[self.stations[-1]] = c
                    self.scheduled_times[self.stations[-1]] = d
                else:
                    self.is_done[origin_station] = True
                    self.is_done[self.stations[-1]] = True

                # only look at the next n_stations that aren't yet done to be as
                # friendly as possible to the API. The is_first_time fanciness
                # is intended to make it possible to debug trains that are
                # currently running down the track but have already started
                if is_first_time:
                    if all((
                        self.next_station is None,
                        self.tracked_times[origin_station] is not None,
                        not self.is_done[origin_station],
                    )):
                        self.next_station = origin_station
                else:
                    self.next_station = self.next_station or origin_station
                    n += 1
                if n >= self.n_stations:
                    break

    def pause(self):
        """pause for a bit before making another round of requests. to be as
        friendly to the API as possible, this tunes the time to be the
        maximum of the specified min_sleep_time or half of the time to the
        next train's estimated arrival
        """
        now = datetime.datetime.now()
        next_time = self.tracked_times[self.next_station]
        if next_time < now:
            sleep_time = self.min_sleep_time
        else:
            dt = self.tracked_times[self.next_station] - datetime.datetime.now()
            sleep_time = max(self.min_sleep_time, dt.seconds/2)
        self.countdown(sleep_time, self.next_station)

    def countdown(self, sleep_time, next_station):
        for i in range(sleep_time, 0, -1):
            sys.stdout.write((
                "Next stop %(next_station)s. "
                "Repinging API in %(i)3d seconds...\r"
            ) % locals())
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write('\n')

    def update_progress(self, stream=None):
        stream = stream or sys.stdout
        for station in self.stations:
            done = ' '
            if self.is_done[station]:
                done = u"\u2713"
            if None in (self.tracked_times[station], self.scheduled_times[station]):
                dt = ""
            else:
                dt = self.tracked_times[station] - self.scheduled_times[station]
                dt = dt.seconds/60
                if dt>0:
                    dt = "+" + str(dt) + " late"
                else:
                    dt = str(dt) + " early"
            s = "%s %20s %21s %21s  %s" % (
                done, station, self.tracked_times[station],
                self.scheduled_times[station], dt
            )
            stream.write(s.encode('utf-8') + '\n')
        stream.write('\n')

    def get_error_message(self, origin):
        trip_id = self.trip_id
        started_script = self.started_script
        destination = self.stations[-1]
        msg = (
            'Script started at %(started_script)s.\n'
            'Exception raised when querying the rail time tracker for trip '
            '%(trip_id)s traveling from %(origin)s to %(destination)s. \n\n'
        ) % locals()
        stream = StringIO.StringIO()
        self.update_progress(stream=stream)
        msg += stream.getvalue() + '\n\n'
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

    def query_rail_time_tracker(self, origin):
        # prepare the post data to the API
        request_data = {
            "line": self.route,
            "origin": origin,
            "destination": self.stations[-1],
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
            if int(train['train_num']) == self.train_number:
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

        return (
            tracked_departure_time, scheduled_departure_time,
            tracked_arrival_time, scheduled_arrival_time,
        )

    def cast_as_time(self, time_as_string):
        t = datetime.datetime.strptime(time_as_string, "%I:%M%p")
        today = datetime.date.today()
        return t.replace(today.year, today.month, today.day)

    def save_punchcards(self):

        route_id = gtfs.get_route(self.trip_id)
        route = Route.objects.get(pk=route_id)

        for stop_id in self.stations:
            station = Station.objects.get(stop_id=stop_id, route=route)
            punchcard = Punchcard(
                trip_id=self.trip_id,
                station=station,
                scheduled_time=self.scheduled_times[stop_id],
                tracked_time=self.tracked_times[stop_id],
            )
            punchcard.save()

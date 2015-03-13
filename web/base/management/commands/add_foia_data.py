import os
import csv
import datetime
import collections

from django.conf import settings

from ..gtfs_commands import BaseCommand
from base.models import Punchcard, Station, Route
from base import gtfs

class Command(BaseCommand):
    help = (
        "put the data from FOIA request into the database. useful for having "
        "a reliable test set"
    )

    foia_csv = os.path.join(BaseCommand.data_dir, 'foia_arrival_departure.csv')


    _version_cache = {}
    def create_version_cache(self):
        with gtfs.CsvReader(self.stop_times_txt) as reader:
            for row in reader:
                route, number, version = gtfs.get_train_info(row['trip_id'])
                # do not use collections.defaultdict to make this throw errors
                # in the right way when something isn't in the cache
                try:
                    self._version_cache[route][number] = version
                except KeyError:
                    self._version_cache[route] = {number: version}

    def get_train_id_version(self, route, train_number):
        if not self._version_cache:
            self.create_version_cache()
        return self._version_cache[route][train_number]


    _stop_cache = {}
    def create_stop_cache(self):
        with gtfs.CsvReader(self.stops_txt) as reader:
            for row in reader:
                self._stop_cache[row['stop_name']] = row['stop_id']

    def get_stop_id(self, stop_name):
        if not self._stop_cache:
            self.create_stop_cache()
        return self._stop_cache[stop_name]

    _schedule_cache = {}
    def create_schedule_cache(self):
        with gtfs.CsvReader(self.stop_times_txt) as reader:
            for row in reader:
                x = row['departure_time'].split(':')
                if int(x[0]) >=24:
                    x[0] = str(int(x[0]) - 24)
                t = datetime.datetime.strptime(':'.join(x), '%H:%M:%S')
                # do not use collections.defaultdict to make this throw errors
                # in the right way when something isn't in the cache
                try:
                    self._schedule_cache[row['trip_id']][row['stop_id']] = t
                except KeyError:
                    self._schedule_cache[row['trip_id']] = {row['stop_id']: t}

    def get_scheduled_time(self, trip_id, stop_id):
        if not self._schedule_cache:
            self.create_schedule_cache()
        return self._schedule_cache[trip_id][stop_id]

    def convert_datetime(self, s):
        return datetime.datetime.strptime(s, '%m/%d/%y %H:%M')

    def handle(self, *args, **kwargs):

        # this is only loading UP-W data at the moment

        # go through the FOIA data and load the UP-W data into the database
        with gtfs.CsvReader(self.foia_csv) as reader:
            route = Route.objects.get(pk="UP-W")
            for row in reader:
                if row['Corridor'] == 'UP West' and row['Train Number'].isdigit():
                    trip_id = "UP-W_UW%s_%s" % (
                        row['Train Number'],
                        self.get_train_id_version("UP-W", int(row['Train Number'])),
                    )
                    stop_id = self.get_stop_id(row['Station'])
                    tracked_time = self.convert_datetime(row['Departure Date/Time'])
                    try:
                        scheduled_time = self.get_scheduled_time(trip_id, stop_id)
                    except KeyError:
                        print "UNSCHEDULED STOP", trip_id, stop_id
                        continue # some random trains make unscheduled stops, apparently?
                    scheduled_time = scheduled_time.replace(
                        tracked_time.year, tracked_time.month, tracked_time.day,
                    )

                    station = Station.objects.get(stop_id=stop_id, route=route)
                    punchcard, created = Punchcard.objects.get_or_create(
                        trip_id=trip_id,
                        station=station,
                        scheduled_time=scheduled_time,
                        tracked_time=tracked_time,
                    )

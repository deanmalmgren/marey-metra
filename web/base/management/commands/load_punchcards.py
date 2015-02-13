import os
import csv

from django.core.management.base import BaseCommand

from base.models import Punchcard, Station
from base import gtfs

class Command(BaseCommand):
    args = '<csv_filename>'
    help = "load data that is dumped from the dump_punchcards command"

    def handle(self, *args, **kwargs):
        csv_filename = args[0]


        # create a cache of all the stations to make it easy to insert things
        station_cache = {}
        for station in Station.objects.iterator():
            station_cache[(station.route.id, station.stop_id)] = station

        # add the data one punchcard at a time
        #
        # TODO: this can probably be made much more efficient with LOAD DATA
        # INFILE fanciness
        with open(csv_filename) as stream:
            reader = csv.reader(stream)
            for row in reader:
                route_id = gtfs.get_route(row[0])
                key = (route_id, row[1])
                punchcard, created = Punchcard.objects.get_or_create(
                    trip_id=row[0],
                    station=station_cache[key],
                    scheduled_time=row[2],
                    tracked_time=row[3],
                )

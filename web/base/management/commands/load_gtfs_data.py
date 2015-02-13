import os

from base.management.gtfs_commands import BaseCommand
from base import gtfs
from base.models import Route, Station

class Command(BaseCommand):
    help = "this management command loads in all of the relevant gtfs data"

    def handle(self, *args, **kwargs):

        # load the Route table
        route_cache = {}
        with gtfs.CsvReader(self.routes_txt) as reader:
            for row in reader:
                route, created = Route.objects.get_or_create(
                    id=row['route_id'],
                )
                route_cache[row['route_id']] = route

        # get the distances from chicago and the endpoint
        distances_from_chicago = self.get_distances_from_chicago()
        distances_from_endpoint = {}
        for route, distances in distances_from_chicago.iteritems():
            distances_from_endpoint[route] = {}
            endpoint_distance = max(distances.values())
            for stop_id, distance in distances.iteritems():
                distances_from_endpoint[route][stop_id] = endpoint_distance - distance

        # load the Station table
        with gtfs.CsvReader(self.stop_times_txt) as reader:
            for row in reader:
                route_id = gtfs.get_route(row['trip_id'])
                x = distances_from_chicago[route_id][row['stop_id']]
                y = distances_from_endpoint[route_id][row['stop_id']]
                station, created = Station.objects.get_or_create(
                    route=route_cache[route_id],
                    stop_id=row['stop_id'],
                    distance_from_chicago=x,
                    distance_from_endpoint=y,
                )

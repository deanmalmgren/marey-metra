import os
import collections

from shapely.geometry import LineString, Point
from geopy.distance import vincenty

from django.core.management.base import BaseCommand as DjangoBaseCommand
from django.conf import settings

from base.models import Punchcard
from base import gtfs


def _cut(line, point):
    """Cuts a line in two at a distance from its starting point. Adapted from:
    http://toblerity.org/shapely/manual.html#linear-referencing-methods
    """
    distance = line.project(point)
    if distance <= 0.0:
        return [LineString(), LineString(line)]
    if distance >= line.length:
        return [LineString(line), LineString()]
    coords = list(line.coords)
    for i, p in enumerate(coords):
        pd = line.project(Point(p))
        if pd == distance:
            return [
                LineString(coords[:i+1]),
                LineString(coords[i:])]
        if pd > distance:
            cp = line.interpolate(distance)
            return [
                LineString(coords[:i] + [(cp.x, cp.y)]),
                LineString([(cp.x, cp.y)] + coords[i:])]

def _distance_to_point_along_path(point, path):
    result = _cut(path, point)
    points = list(result[0].coords)
    distance = 0.0
    for p1, p2 in zip(points[:-1], points[1:]):
        distance += vincenty(p1, p2).miles
    return distance


class BaseCommand(DjangoBaseCommand):

    # this sets up some really trivial data files that are useful for reading
    data_dir = os.path.abspath(os.path.join(settings.PROJECT_ROOT,'..','data'))
    gtfs_dir = os.path.join(data_dir, 'metra_gtfs')
    stop_times_txt = os.path.join(gtfs_dir, 'stop_times.txt')
    stops_txt = os.path.join(gtfs_dir, 'stops.txt')
    shapes_txt = os.path.join(gtfs_dir, 'shapes.txt')
    routes_txt = os.path.join(gtfs_dir, 'routes.txt')


    def get_distances_from_chicago(self):
        """This calculates the distance from chicago for each stop along every
        route. The paths of each train route and the station locations are
        grabbed from GTFS data.
        """

        # collect all of the route path information
        route_paths = {}
        with gtfs.CsvReader(self.shapes_txt) as reader:
            for row in reader:
                latitude = float(row['shape_pt_lat'])
                longitude = float(row['shape_pt_lon'])
                route, io, v = row['shape_id'].split('_')
                if io == "OB":
                    if not route_paths.has_key(route):
                        route_paths[route] = {}
                    if not route_paths[route].has_key(v):
                        route_paths[route][v] = []
                    route_paths[route][v].append((latitude, longitude))

        # convert all the route_path lists to shapely objects
        for route in route_paths:
            for v, point_list in route_paths[route].iteritems():
                route_paths[route][v] = LineString(point_list)

        # get the coordinates of all the stations
        stop_positions = {}
        with gtfs.CsvReader(self.stops_txt) as reader:
            for row in reader:
                latitude = float(row['stop_lat'])
                longitude = float(row['stop_lon'])
                stop_positions[row['stop_id']] = Point(latitude, longitude)

        # calculate the distance from chicago for all of the stops
        distances_from_chicago = {}
        with gtfs.CsvReader(self.stop_times_txt) as reader:
            for row in reader:
                route = gtfs.get_route(row['trip_id'])
                stop_id = row['stop_id']
                if not distances_from_chicago.has_key(route):
                    distances_from_chicago[route] = {}
                if not distances_from_chicago[route].has_key(stop_id):
                    is_intersecting = False
                    for v, path in route_paths[route].iteritems():
                        if stop_positions[stop_id].intersects(path):
                            distance = _distance_to_point_along_path(
                                stop_positions[stop_id],
                                path,
                            )
                            distances_from_chicago[route][stop_id] = distance
                            is_intersecting = True
                            break
                    if not is_intersecting:
                        raise ValueError("crap. station isn't on any paths")

        return distances_from_chicago

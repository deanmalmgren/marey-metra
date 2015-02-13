import os
import collections

from django.core.management.base import BaseCommand as DjangoBaseCommand
from django.conf import settings

from base.models import Punchcard
from base import gtfs

class BaseCommand(DjangoBaseCommand):

    # this sets up some really trivial data files that are useful for reading
    data_dir = os.path.abspath(os.path.join(settings.PROJECT_ROOT,'..','data'))
    gtfs_dir = os.path.join(data_dir, 'metra_gtfs')
    stop_times_txt = os.path.join(gtfs_dir, 'stop_times.txt')
    stops_txt = os.path.join(gtfs_dir, 'stops.txt')
    shapes_txt = os.path.join(gtfs_dir, 'shapes.txt')
    routes_txt = os.path.join(gtfs_dir, 'routes.txt')


    def get_distances_from_chicago(self):
        # load in the stations along the UP-W line and their corresponding
        # stop index (which is how the distances are stored)
        #
        # NOTE: all outbound trains are odd and metra has configured their GTFS
        # data to use the index in the stop_sequence to correspond with the same
        # index in the shapes.txt file for telling the distance from the start
        # of the route
        stops = {}
        with gtfs.CsvReader(self.stop_times_txt) as reader:
            for row in reader:
                route, train_number, _ = gtfs.get_train_info(row['trip_id'])
                stop_id = row['stop_id']
                stop_sequence = int(row['stop_sequence'])
                if train_number % 2 == 1:
                    if not stops.has_key(route):
                        stops[route] = {}
                    if not stops[route].has_key(stop_id):
                        stops[route][stop_id] = stop_sequence
                    elif stops[route][stop_id] != stop_sequence:
                        pass # see TODO below
                        # print >> sys.stderr, "SHIT", route, stop_id, stops[route][stop_id], stop_sequence
                        # raise Exception("oh shit...didn't expect that")

        # TODO: this is a *big* placeholder for getting this properly set up.
        # the distances in the GTFS data are not consistent between routes (lots
        # of 'SHIT' is printed out above). probably want to try using shapely
        # and/or a request to Metra to make their GTFS feeds publicly available
        # https://code.google.com/p/googletransitdatafeed/wiki/PublicFeeds#How_to_add_a_feed_to_this_page
        distances_from_chicago = collections.defaultdict(dict)
        for route, _stops in stops.iteritems():
            for stop_id, stop_sequence in _stops.iteritems():
                distances_from_chicago[route][stop_id] = stop_sequence
        return distances_from_chicago

        #
        #
        # NOTE: THe following would work, but the stop_sequence is not
        # consistent across routes, which gives me doubts that it properly lines
        # up with the actual data in the shapes.txt file
        #
        #

        # # need the reverse mapping below
        # reverse_stops = {}
        # for route, _stops in stops.iteritems():
        #     reverse_stops[route] = {}
        #     for stop_id, stop_sequence in _stops.iteritems():
        #         reverse_stops[route][stop_sequence] = stop_id
        #
        # # load in the distances for the UP-W line and match them up with the
        # # stations
        # distances_from_chicago = collections.defaultdict(dict)
        # with gtfs.CsvReader(self.shapes_txt) as reader:
        #     for row in reader:
        #         route = row['shape_id'].split('_')[0]
        #         is_outbound = row['shape_id'].split('_')[1] == 'OB'
        #         if is_outbound:
        #             stop_sequence = int(row['shape_pt_sequence'])
        #             stop_id = reverse_stops[route][stop_sequence]
        #             distance = float(row['shape_dist_traveled'])
        #             print route, stop_id, distance
        #             distances_from_chicago[route][stop_id] = distance
        # print distances_from_chicago
        # return distances_from_chicago

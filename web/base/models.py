""" Basic models, such as user profile """

from django.db import models

import gtfs

class Route(models.Model):
    """This is something like UP-W"""
    id = models.CharField(max_length=255, primary_key=True)

class Station(models.Model):
    """This is used to store information about particular stations, which is
    kinda like the GTFS version of `stop` except a Station belongs to one route.
    """
    class Meta:
        unique_together = ('route', 'stop_id')
        ordering = ('route', 'distance_from_chicago')
    route = models.ForeignKey(Route)
    stop_id = models.CharField(max_length=255)
    distance_from_chicago = models.FloatField()
    distance_from_endpoint = models.FloatField()

class Punchcard(models.Model):
    """there are some really obvious ways to normalize this database to be
    better, but this is a damn easy way to get started storing the data.

    This table is intended to mash together data from shapes.txt,
    stop_times.txt, and the Metra Rail Time Tracker
    """
    trip_id = models.CharField(
        max_length=63,
        help_text="trip_id is a mashup of lots of things",
        db_index=True,
    )
    station = models.ForeignKey(Station)
    scheduled_time = models.DateTimeField(
        help_text="the scheduled departure time according to stop_times.txt",
    )
    tracked_time = models.DateTimeField(
        help_text=(
            "the last 'estimated' departure time that is captured from the "
            "rail time tracker"
        ),
    )

    @property
    def train_number(self):
        return gtfs.get_train_number(self.trip_id)

    @property
    def version(self):
        return gtfs.get_version(self.trip_id)

    def to_json_dict(self):
        return {
            "stop_id": self.station.stop_id,
            "scheduled_time": self.scheduled_time,
            "tracked_time": self.tracked_time,
            "distance_from_chicago": self.station.distance_from_chicago,
        }

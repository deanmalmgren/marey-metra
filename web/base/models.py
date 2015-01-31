""" Basic models, such as user profile """

from django.db import models

import gtfs

class Route(models.Model):
    """This is something like UP-W"""
    name = models.CharField(max_length=255, unique=True)

class Station(models.Model):
    """This is used to store information about particular stations"""
    class Meta:
        unique_together = ('route', 'name')
        order_by = ('route', 'distance_from_chicago')
    route = models.ForeignKey(Route)
    name = models.CharField(max_length=255)
    distance_from_chicago = models.FloatField()
    distance_from_endpoint = models.FloatField()

class Schedule(models.Model):
    """This is used to store the schedule information that is downloaded from
    GTFS
    """
    class Meta:
        pass

    DAY_CHOICES = (
        ("weekday", "weekday"),
        ("saturday", "saturday"),
        ("sunday", "sunday"),
        ("weekend", "weekend"),
    )

    id = models.CharField(max_length=31, primary_key=True, help_text="example: UP-W_UW38_V1")
    route = models.ForeignKey(Route)
    station = models.ForeignKey(Station)
    time = models.CharField(max_length=5, help_text="HH:MM")
    days = models.CharField(choices=DAY_CHOICES)

    # XXXX NOT SURE I LIKE THE IDEA OF STORING THE time AND days IN THE
    # DATABASE. ITS KINDA NICE TO BE ABLE TO HAVE THE DATETIME STORED ON THE
    # PUNCHCARD FOR QUICK SUBTRACTION OF DATE OBJECTS...

    @property
    def train_number(self):
        return gtfs.get_train_number(self.id)
    @property
    def version(self):
        return gtfs.get_version(self.id)

class Punchcard(models.Model):
    """there are some really obvious ways to normalize this database to be
    better, but this is a damn easy way to get started storing the data.

    This table is intended to mash together data from shapes.txt,
    stop_times.txt, and the Metra Rail Time Tracker
    """

    trip_id = models.CharField(
        max_length=63,
        help_text="trip_id is a mashup of lots of things"
    )
    distance_traveled = models.FloatField(
        help_text=(
            "distance from start of the Trip from shapes.txt, "
            "measured in miles"
        ),
    )
    stop_id = models.CharField(
        max_length=63,
        help_text="the stop_id (station name) from stop_times.txt",
    )
    scheduled_time = models.DateTimeField(
        help_text="the scheduled departure time according to stop_times.txt",
    )
    tracked_time = models.DateTimeField(
        help_text=(
            "the last 'estimated' departure time that is captured from the "
            "rail time tracker"
        ),
    )

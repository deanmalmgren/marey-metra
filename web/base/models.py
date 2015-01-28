""" Basic models, such as user profile """

from django.db import models


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

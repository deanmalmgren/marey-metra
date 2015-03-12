import csv
import sys

from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.utils import timezone

class Command(BaseCommand):
    help = "dump the punchcard data into csv format (to help with migrating db)"


    def handle(self, *args, **kwargs):

        # using a database connection because its a lot faster
        cursor = connection.cursor()
        cursor.execute("""
        SELECT punchcard.trip_id, station.stop_id, punchcard.scheduled_time, punchcard.tracked_time
        FROM base_punchcard AS punchcard, base_station AS station
        WHERE punchcard.station_id=station.id
        """)
        writer = csv.writer(sys.stdout)
        writer.writerow(['trip_id','stop_id', 'scheduled_time', 'tracked_time'])
        for row in cursor:
            if None not in row[2:]:
                writer.writerow(list(row[:2]) + map(timezone.localtime, row[2:]))

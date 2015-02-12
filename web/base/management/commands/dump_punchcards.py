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
        SELECT trip_id, stop_id, scheduled_time, tracked_time
        FROM base_punchcard
        """)
        writer = csv.writer(sys.stdout)
        writer.writerow(['trip_id','stop_id', 'scheduled_time', 'tracked_time'])
        for row in cursor:
            writer.writerow(list(row[:2]) + map(timezone.localtime, row[2:]))

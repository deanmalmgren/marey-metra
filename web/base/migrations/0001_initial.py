# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Punchcard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('trip_id', models.CharField(help_text=b'trip_id is a mashup of lots of things', max_length=63)),
                ('distance_traveled', models.FloatField(help_text=b'distance from start of the Trip from shapes.txt, measured in miles')),
                ('stop_id', models.CharField(help_text=b'the stop_id (station name) from stop_times.txt', max_length=63)),
                ('scheduled_departure_time', models.DateTimeField(help_text=b'the scheduled departure time according to stop_times.txt')),
                ('tracker_departure_time', models.DateTimeField(help_text=b"the last 'estimated' departure time that is captured from the rail time tracker")),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

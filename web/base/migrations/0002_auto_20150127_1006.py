# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='punchcard',
            old_name='scheduled_departure_time',
            new_name='scheduled_time',
        ),
        migrations.RenameField(
            model_name='punchcard',
            old_name='tracker_departure_time',
            new_name='tracked_time',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_auto_20150212_0422'),
    ]

    operations = [
        migrations.AlterField(
            model_name='punchcard',
            name='trip_id',
            field=models.CharField(help_text=b'trip_id is a mashup of lots of things', max_length=63, db_index=True),
            preserve_default=True,
        ),
    ]

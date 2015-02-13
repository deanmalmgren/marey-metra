# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_auto_20150212_0426'),
    ]

    operations = [
        migrations.RenameField(
            model_name='station',
            old_name='name',
            new_name='stop_id',
        ),
        migrations.RemoveField(
            model_name='route',
            name='name',
        ),
        migrations.AlterField(
            model_name='route',
            name='id',
            field=models.CharField(max_length=255, serialize=False, primary_key=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='station',
            unique_together=set([('route', 'stop_id')]),
        ),
    ]

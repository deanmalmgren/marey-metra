# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_auto_20150127_1006'),
    ]

    operations = [
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('distance_from_chicago', models.FloatField()),
                ('distance_from_endpoint', models.FloatField()),
                ('route', models.ForeignKey(to='base.Route')),
            ],
            options={
                'ordering': ('route', 'distance_from_chicago'),
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='station',
            unique_together=set([('route', 'name')]),
        ),
        migrations.RemoveField(
            model_name='punchcard',
            name='distance_traveled',
        ),
        migrations.RemoveField(
            model_name='punchcard',
            name='stop_id',
        ),
        migrations.AddField(
            model_name='punchcard',
            name='station',
            field=models.ForeignKey(default=None, to='base.Station'),
            preserve_default=False,
        ),
    ]

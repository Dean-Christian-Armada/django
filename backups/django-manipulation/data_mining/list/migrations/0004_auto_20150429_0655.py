# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0003_auto_20150429_0334'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('activity', models.CharField(max_length=100, null=True)),
                ('description', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='members',
            name='date_added',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 29, 6, 55, 46, 747160, tzinfo=utc), editable=False),
        ),
        migrations.AddField(
            model_name='members',
            name='date_modified',
            field=models.DateTimeField(null=True, editable=False),
        ),
    ]

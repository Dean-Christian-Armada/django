# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0004_auto_20150429_0655'),
    ]

    operations = [
        migrations.AddField(
            model_name='dashboard',
            name='user',
            field=models.ForeignKey(default=1, to='list.Users'),
        ),
        migrations.AddField(
            model_name='users',
            name='userlevel',
            field=models.ForeignKey(default=1, to='list.Userlevel'),
        ),
        migrations.AlterField(
            model_name='members',
            name='date_added',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 29, 8, 21, 22, 896918, tzinfo=utc), editable=False),
        ),
    ]

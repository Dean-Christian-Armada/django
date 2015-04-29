# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0005_auto_20150429_0821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='members',
            name='date_added',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 29, 8, 27, 19, 759409, tzinfo=utc), editable=False),
        ),
    ]

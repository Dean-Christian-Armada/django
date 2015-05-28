# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0006_auto_20150429_0827'),
    ]

    operations = [
        migrations.AlterField(
            model_name='members',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

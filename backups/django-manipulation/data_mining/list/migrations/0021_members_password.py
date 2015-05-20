# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0020_auto_20150520_0621'),
    ]

    operations = [
        migrations.AddField(
            model_name='members',
            name='password',
            field=models.CharField(default=b'sample', max_length=100),
        ),
    ]

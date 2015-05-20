# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0022_auto_20150520_0628'),
    ]

    operations = [
        migrations.AddField(
            model_name='members',
            name='password',
            field=models.CharField(default=b'sample', max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='members',
            name='username',
            field=models.CharField(max_length=100, null=True),
        ),
    ]

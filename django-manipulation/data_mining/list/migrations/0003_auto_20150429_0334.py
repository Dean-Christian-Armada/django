# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0002_auto_20150429_0332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='members',
            name='gender',
            field=models.CharField(max_length=100, null=True, choices=[(b'M', b'Male'), (b'F', b'Female')]),
        ),
    ]

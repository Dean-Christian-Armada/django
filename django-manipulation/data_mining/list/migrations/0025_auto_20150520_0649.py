# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0024_auto_20150520_0648'),
    ]

    operations = [
        migrations.AlterField(
            model_name='members',
            name='password',
            field=models.CharField(default=b'sample', max_length=100, null=True),
        ),
    ]

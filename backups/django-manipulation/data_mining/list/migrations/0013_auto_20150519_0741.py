# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0012_auto_20150519_0740'),
    ]

    operations = [
        migrations.AlterField(
            model_name='members',
            name='code',
            field=models.CharField(default=b'dean', max_length=4),
        ),
    ]

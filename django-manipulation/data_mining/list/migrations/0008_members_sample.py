# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0007_auto_20150429_0833'),
    ]

    operations = [
        migrations.AddField(
            model_name='members',
            name='sample',
            field=models.CharField(default=2, max_length=30),
            preserve_default=False,
        ),
    ]

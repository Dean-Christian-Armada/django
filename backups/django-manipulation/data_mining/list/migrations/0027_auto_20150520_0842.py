# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0026_auto_20150520_0650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='members',
            name='username',
            field=models.CharField(max_length=100, unique=True, null=True),
        ),
    ]

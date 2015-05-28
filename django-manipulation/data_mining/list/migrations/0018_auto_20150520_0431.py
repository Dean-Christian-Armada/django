# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0017_auto_20150520_0411'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marines',
            name='members',
            field=models.OneToOneField(to='list.Members'),
        ),
    ]

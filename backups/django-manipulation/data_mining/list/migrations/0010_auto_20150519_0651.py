# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0009_remove_members_sample'),
    ]

    operations = [
        migrations.AlterField(
            model_name='members',
            name='name',
            field=models.CharField(max_length=100, unique=True, null=True),
        ),
    ]

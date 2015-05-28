# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0008_members_sample'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='members',
            name='sample',
        ),
    ]

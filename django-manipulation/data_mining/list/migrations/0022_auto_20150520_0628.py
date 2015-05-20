# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0021_members_password'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='members',
            name='password',
        ),
        migrations.RemoveField(
            model_name='members',
            name='username',
        ),
    ]

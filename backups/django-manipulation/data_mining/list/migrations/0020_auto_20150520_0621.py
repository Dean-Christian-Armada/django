# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0019_members_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='members',
            name='user',
        ),
        migrations.AddField(
            model_name='members',
            name='username',
            field=models.CharField(default=b'sample', max_length=100),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0029_auto_20150521_0221'),
    ]

    operations = [
        migrations.AddField(
            model_name='members',
            name='old_password',
            field=models.CharField(max_length=100, null=True),
        ),
    ]

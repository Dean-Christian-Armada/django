# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0030_members_old_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='members',
            name='password',
            field=models.CharField(max_length=100, null=True, editable=False),
        ),
    ]

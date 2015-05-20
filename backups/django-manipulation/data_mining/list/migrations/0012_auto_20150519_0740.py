# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0011_members_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='members',
            name='code',
            field=models.CharField(default=b'dean', max_length=4, editable=False),
        ),
    ]

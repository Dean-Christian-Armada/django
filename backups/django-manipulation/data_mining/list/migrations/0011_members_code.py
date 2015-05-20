# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0010_auto_20150519_0651'),
    ]

    operations = [
        migrations.AddField(
            model_name='members',
            name='code',
            field=models.CharField(default=b'RVAE', max_length=4, editable=False),
        ),
    ]

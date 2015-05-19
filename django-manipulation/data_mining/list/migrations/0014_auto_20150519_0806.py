# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0013_auto_20150519_0741'),
    ]

    operations = [
        migrations.AlterField(
            model_name='members',
            name='code',
            field=models.CharField(unique=True, max_length=4, editable=False),
        ),
        migrations.AlterField(
            model_name='members',
            name='title',
            field=models.CharField(max_length=5, null=True, choices=[(b'Mr.', b'Mr.'), (b'Ms.', b'Ms.'), (b'Mrs.', b'Mrs.')]),
        ),
    ]

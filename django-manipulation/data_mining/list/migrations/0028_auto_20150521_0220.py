# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0027_auto_20150520_0842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marines',
            name='cert_name',
            field=models.CharField(default=b'N/A', max_length=100),
        ),
        migrations.AlterField(
            model_name='marines',
            name='cert_number',
            field=models.CharField(default=b'N/A', max_length=20),
        ),
        migrations.AlterField(
            model_name='marines',
            name='picture',
            field=models.ImageField(upload_to=b'/profile_images/', blank=True),
        ),
    ]

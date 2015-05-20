# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0015_auto_20150520_0208'),
    ]

    operations = [
        migrations.AddField(
            model_name='marines',
            name='picture',
            field=models.ImageField(upload_to=b'profile_images', blank=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0028_auto_20150521_0220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marines',
            name='picture',
            field=models.ImageField(upload_to=b'profile_images', blank=True),
        ),
    ]

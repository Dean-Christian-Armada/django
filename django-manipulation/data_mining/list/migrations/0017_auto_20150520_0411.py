# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0016_marines_picture'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='marines',
            options={'verbose_name_plural': 'Certificates'},
        ),
        migrations.AlterModelOptions(
            name='members',
            options={'verbose_name_plural': 'Bio'},
        ),
        migrations.AlterField(
            model_name='members',
            name='code',
            field=models.CharField(max_length=4, editable=False),
        ),
    ]

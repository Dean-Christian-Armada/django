# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('list', '0014_auto_20150519_0806'),
    ]

    operations = [
        migrations.CreateModel(
            name='Marines',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cert_name', models.CharField(max_length=100, null=True)),
                ('cert_number', models.CharField(max_length=10, null=True)),
                ('date_issue', models.DateField(null=True)),
                ('date_expire', models.DateField(null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='users',
            name='user',
        ),
        migrations.RemoveField(
            model_name='users',
            name='userlevel',
        ),
        migrations.RemoveField(
            model_name='dashboard',
            name='user',
        ),
        migrations.AddField(
            model_name='dashboard',
            name='members',
            field=models.ForeignKey(default=1, to='list.Members'),
        ),
        migrations.AddField(
            model_name='members',
            name='userlevel',
            field=models.ForeignKey(default=1, to='list.Userlevel'),
        ),
        migrations.AlterField(
            model_name='userlevel',
            name='userlevel',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.DeleteModel(
            name='Users',
        ),
        migrations.AddField(
            model_name='marines',
            name='members',
            field=models.ForeignKey(to='list.Members'),
        ),
    ]

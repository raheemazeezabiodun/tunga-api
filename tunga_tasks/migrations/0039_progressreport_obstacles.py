# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-01-03 05:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tunga_tasks', '0038_auto_20161222_0918'),
    ]

    operations = [
        migrations.AddField(
            model_name='progressreport',
            name='obstacles',
            field=models.TextField(blank=True, null=True),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2018-01-13 09:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tunga_tasks', '0150_auto_20180105_0655'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='dev_pay_rate',
            field=models.DecimalField(blank=True, decimal_places=4, default=None, max_digits=19, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='pm_pay_rate',
            field=models.DecimalField(blank=True, decimal_places=4, default=None, max_digits=19, null=True),
        ),
    ]

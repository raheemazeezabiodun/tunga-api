# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-01 15:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tunga_tasks', '0102_auto_20170531_0240'),
    ]

    operations = [
        migrations.AddField(
            model_name='progressreport',
            name='next_deadline_fail_reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]
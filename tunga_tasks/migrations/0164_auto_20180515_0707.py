# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-05-15 07:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tunga_tasks', '0163_auto_20180301_0711'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='payment_reminder_escalated_sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='payment_reminder_sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

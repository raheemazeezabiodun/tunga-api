# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-19 18:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tunga_tasks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='paid',
            field=models.BooleanField(default=False),
        ),
    ]
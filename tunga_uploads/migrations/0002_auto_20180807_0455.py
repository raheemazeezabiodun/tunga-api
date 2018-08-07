# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-07 04:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tunga_uploads', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='upload',
            name='legacy_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='upload',
            name='migrated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

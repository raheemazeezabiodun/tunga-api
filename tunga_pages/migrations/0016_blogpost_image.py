# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2018-02-15 15:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tunga_pages', '0015_blogpost_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='blog/%Y/%m/%d'),
        ),
    ]

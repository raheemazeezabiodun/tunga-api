# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2018-02-15 05:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tunga_pages', '0013_blogpost'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='published',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='published_at',
            field=models.DateTimeField(null=True),
        ),
    ]

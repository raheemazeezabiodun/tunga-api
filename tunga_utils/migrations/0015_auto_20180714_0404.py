# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-14 04:04
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tunga_utils', '0014_auto_20180515_0707'),
    ]

    operations = [
        migrations.AlterField(
            model_name='upload',
            name='content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='legacy_uploads', to='contenttypes.ContentType', verbose_name='content type'),
        ),
        migrations.AlterField(
            model_name='upload',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='legacy_uploads', to=settings.AUTH_USER_MODEL),
        ),
    ]

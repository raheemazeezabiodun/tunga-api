# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2018-04-12 01:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tunga_pages', '0019_auto_20180412_0112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skillpage',
            name='skill',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='tunga_profiles.Skill'),
        ),
    ]
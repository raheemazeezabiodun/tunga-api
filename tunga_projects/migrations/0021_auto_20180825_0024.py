# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-25 00:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tunga_projects', '0020_auto_20180807_0455'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='participation',
            options={'ordering': ['-created_at'], 'verbose_name_plural': 'participation'},
        ),
        migrations.AlterModelOptions(
            name='progressreport',
            options={'ordering': ['-created_at']},
        ),
        migrations.AddField(
            model_name='project',
            name='stage',
            field=models.CharField(choices=[(b'opportunity', b'Opportunity'), (b'active', b'Active')], default=b'active', max_length=20),
        ),
    ]

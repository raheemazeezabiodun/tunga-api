# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-07-27 04:02
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tunga_tasks', '0120_auto_20170726_0145'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='multitaskpaymentkey',
            name='amount',
        ),
    ]

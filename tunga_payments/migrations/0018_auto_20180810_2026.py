# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-10 20:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tunga_payments', '0017_auto_20180809_0618'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='status',
            field=models.CharField(choices=[(b'initiated', 'Initiated'), (b'completed', 'Completed'), (b'failed', 'Failed'), (b'retry', 'Retry')], default=b'initiated', max_length=50),
        ),
        migrations.AlterField(
            model_name='payment',
            name='currency',
            field=models.CharField(choices=[(b'EUR', b'EUR')], default=b'EUR', max_length=15),
        ),
    ]

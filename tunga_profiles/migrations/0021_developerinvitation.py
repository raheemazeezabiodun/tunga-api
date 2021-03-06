# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-12-30 18:22
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import tunga_profiles.validators
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tunga_profiles', '0020_auto_20161222_0918'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeveloperInvitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('email', models.EmailField(max_length=254, unique=True, validators=[tunga_profiles.validators.validate_email])),
                ('invitation_key', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('used', models.BooleanField(default=False)),
                ('used_at', models.DateTimeField(blank=True, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import tagulous.models
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from tunga import settings
from tunga_skills.models import Skill
from tunga_utils.constants import PROJECT_TYPE_CHOICES, PROJECT_TYPE_OTHER, CURRENCY_EUR, \
    PROJECT_EXPECTED_DURATION_CHOICES, CURRENCY_CHOICES_EUR_ONLY


@python_2_unicode_compatible
class Project(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='v2_projects_created', on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=200)
    description = models.TextField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='v2_projects_owned', on_delete=models.DO_NOTHING, blank=True, null=True
    )
    pm = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='v2_projects_managed', on_delete=models.DO_NOTHING, blank=True, null=True
    )
    skills = tagulous.models.TagField(Skill, blank=True)
    budget = models.DecimalField(
        max_digits=19, decimal_places=4, blank=True, null=True, default=None
    )
    currency = models.CharField(max_length=5, choices=CURRENCY_CHOICES_EUR_ONLY, default=CURRENCY_EUR)
    type = models.CharField(max_length=20, choices=PROJECT_TYPE_CHOICES, default=PROJECT_TYPE_OTHER)
    expected_duration = models.CharField(max_length=20, choices=PROJECT_EXPECTED_DURATION_CHOICES, blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    client_survey_enabled = models.BooleanField(default=True)
    pm_updates_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

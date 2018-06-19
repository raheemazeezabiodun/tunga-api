# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import tagulous.models
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from tunga import settings
from tunga_profiles.models import Skill
from tunga_utils.constants import PROJECT_TYPE_CHOICES, PROJECT_TYPE_OTHER, CURRENCY_EUR, \
    PROJECT_EXPECTED_DURATION_CHOICES, CURRENCY_CHOICES_EUR_ONLY, STATUS_INITIAL, REQUEST_STATUS_CHOICES
from tunga_utils.models import Rating


@python_2_unicode_compatible
class Project(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='projects_created', on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=200)
    description = models.TextField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='projects_owned', on_delete=models.DO_NOTHING, blank=True, null=True
    )
    pm = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='projects_managed', on_delete=models.DO_NOTHING, blank=True, null=True
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

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='Participation', through_fields=('project', 'user'),
        related_name='project_participants', blank=True)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Participation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='project_participation', on_delete=models.DO_NOTHING)
    status = models.CharField(
        max_length=20, choices=REQUEST_STATUS_CHOICES,
        help_text=','.join(['%s - %s' % (item[0], item[1]) for item in REQUEST_STATUS_CHOICES]),
        default=STATUS_INITIAL
    )
    updates_enabled = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='project_participants_added')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '#{} | {} - {}'.format(self.id, self.user.get_short_name() or self.user.username, self.project.title)

    class Meta:
        unique_together = ('user', 'project')
        verbose_name_plural = 'participation'

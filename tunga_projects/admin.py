# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from tunga_projects.models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'deadline', 'created_at', 'archived')
    list_filter = ('archived',)
    search_fields = ('title',)

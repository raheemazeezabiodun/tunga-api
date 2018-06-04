# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from tunga_projects.models import Project

admin.site.register(Project)

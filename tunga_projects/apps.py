# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class TungaProjectsConfig(AppConfig):
    name = 'tunga_projects'
    verbose_name = 'Projects'

    def ready(self):
        from actstream import registry
        from tunga_projects import signals

        registry.register(
            self.get_model('Project'), self.get_model('Participation'), self.get_model('Document'),
            self.get_model('ProgressEvent'), self.get_model('ProgressReport')
        )

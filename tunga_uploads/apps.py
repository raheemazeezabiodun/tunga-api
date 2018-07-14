# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class TungaUploadsConfig(AppConfig):
    name = 'tunga_uploads'
    verbose_name = 'Uploads'

    def ready(self):
        from actstream import registry
        from tunga_uploads import signals

        registry.register(self.get_model('Upload'))

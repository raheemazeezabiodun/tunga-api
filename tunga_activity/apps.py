from __future__ import unicode_literals

from django.apps import AppConfig


class TungaActivityConfig(AppConfig):
    name = 'tunga_activity'
    verbose_name = 'Activity Stream'

    def ready(self):
        from actstream import registry
        from tunga_activity import signals

        registry.register(
            self.get_model('FieldChangeLog')
        )

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class TungaPaymentsConfig(AppConfig):
    name = 'tunga_payments'
    verbose_name = 'Payments'

    def ready(self):
        from actstream import registry
        from tunga_tasks import signals

        registry.register(
            self.get_model('Invoice'), self.get_model('Payment')
        )

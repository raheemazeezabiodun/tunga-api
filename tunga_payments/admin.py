# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from tunga_payments.models import Payment, Invoice

admin.site.register(Invoice)
admin.site.register(Payment)

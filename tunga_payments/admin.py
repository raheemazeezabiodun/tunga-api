# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from tunga_payments.models import Payment, Invoice
from tunga_utils.admin import ReadOnlyModelAdmin


@admin.register(Invoice)
class InvoiceAdmin(ReadOnlyModelAdmin):
    list_display = (
        'title', 'type', 'amount', 'milestone', 'issued_at', 'number', 'tax_rate',
        'status', 'paid', 'paid_at', 'archived'
    )
    list_filter = ('type', 'archived', 'paid')
    search_fields = ('project__title', 'title', 'number', 'batch_ref')


@admin.register(Payment)
class InvoiceAdmin(ReadOnlyModelAdmin):
    list_display = ('invoice', 'amount', 'payment_method', 'status', 'paid_at')
    list_filter = ('status',)
    search_fields = ('invoice__title',)

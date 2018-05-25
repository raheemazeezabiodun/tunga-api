# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.contrib.auth.models import User
from django.db import models
from six import python_2_unicode_compatible

from tunga import settings
from tunga_projects.models import Project


@python_2_unicode_compatible
class Invoice(models.Model):
    type_choices = (
        ('client', 'client'),
        ('tunga', 'tunga'),
        ('developer', 'developer'),
    )

    project = models.ForeignKey(to=Project)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='invoice_user', on_delete=models.DO_NOTHING)
    type = models.CharField(max_length=150, choices=type_choices)
    amount = models.IntegerField()
    currency = models.CharField(max_length=15, default='EUR')
    tax_rate = models.IntegerField()
    processing_fee = models.IntegerField()
    created_by = models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='invoice_created_by',
                                   on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)
    number = models.CharField(max_length=150)
    batch_ref = models.CharField(max_length=150, default=uuid.uuid4)

    @property
    def tax_amount(self):
        return (self.amount * self.tax_rate) / 100

    @property
    def paid(self):
        if Payment.objects.filter(invoice_id=self.id).exists():
            return True
        else:
            return False

    def __str__(self):
        return "%s Paid: %s" % (self.project.title, self.paid)


@python_2_unicode_compatible
class Payment(models.Model):
    payment_method_choices = (
        ('stripe', 'stripe'),
        ('bank', 'bank'),
        ('bitcoin', 'bitcoin'),
        ('bitonic', 'bitonic'),
    )
    invoice = models.ForeignKey(to=Invoice, related_name="payment_invoice", on_delete=models.DO_NOTHING)
    amount = models.IntegerField()
    currency = models.CharField(max_length=15, default='EUR')
    payment_method = models.CharField(max_length=150, choices=payment_method_choices)
    paid_at = models.DateTimeField(blank=True)
    created_by = models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='payment_created_by',
                                   on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def type(self):
        if self.invoice.user.is_developer() or self.invoice.user.is_project_manager():
            return "sale"
        elif self.invoice.user.is_project_owner():
            return "purchase"

    def __str__(self):
        return "%s Amount: %s" % (self.invoice.project.title, self.amount)

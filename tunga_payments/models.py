# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import uuid

from django.contrib.auth.models import User
from django.db import models
from dry_rest_permissions.generics import allow_staff_or_superuser
from six import python_2_unicode_compatible

from tunga import settings
from tunga_projects.models import Project, Participation
from tunga_utils.constants import TASK_PAYMENT_METHOD_STRIPE, TASK_PAYMENT_METHOD_BANK, TASK_PAYMENT_METHOD_BITCOIN, \
    TASK_PAYMENT_METHOD_BITONIC, INVOICE_TYPE_CLIENT, INVOICE_TYPE_TUNGA, INVOICE_TYPE_DEVELOPER, STATUS_ACCEPTED


@python_2_unicode_compatible
class Invoice(models.Model):
    type_choices = (
        (INVOICE_TYPE_CLIENT, 'Client'),
        (INVOICE_TYPE_TUNGA, 'Tunga'),
        (INVOICE_TYPE_DEVELOPER, 'Developer'),
    )

    project = models.ForeignKey(to=Project, related_name='invoices_project', on_delete=models.DO_NOTHING)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='invoices_user', on_delete=models.DO_NOTHING)
    type = models.CharField(max_length=150, choices=type_choices)
    amount = models.IntegerField()
    currency = models.CharField(max_length=15, default='EUR')
    tax_rate = models.IntegerField()
    processing_fee = models.IntegerField()
    created_by = models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='invoices_created_by',
                                   on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.CharField(max_length=150, choices=type_choices, null=True, blank=True)
    number = models.CharField(max_length=150)
    batch_ref = models.CharField(max_length=150, default=uuid.uuid4)
    paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True, )
    title = models.CharField(max_length=150, null=True, blank=True, )

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.title:
            self.title = self.project.title
        super(Invoice, self).save(force_insert, force_update, using, update_fields)

    @property
    def tax_amount(self):
        return (self.amount * self.tax_rate) / 100

    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        if request.user == self.user or request.user == self.project.owner:
            return True
        elif request.user.is_project_manager and self.project.pm == request.user:
            return True
        elif request.user.is_project_manager and self.project.user == request.user:
            return True
        elif request.user.is_admin:
            return True
        elif request.user.is_developer and Participation.objects.filter(user=request.user, project=self.project,
                                                                        status=STATUS_ACCEPTED).count() > 0:
            return True
        else:
            return False

    @staticmethod
    @allow_staff_or_superuser
    def has_write_permission(self):
        return False

    @staticmethod
    @allow_staff_or_superuser
    def has_create_permission(self):
        return False

    @staticmethod
    @allow_staff_or_superuser
    def has_update_permission(self):
        return True

    @allow_staff_or_superuser
    def has_object_write_permission(self, request):
        return False

    def __str__(self):
        return "%s Paid: %s" % (self.project.title, self.paid)


@python_2_unicode_compatible
class Payment(models.Model):
    payment_method_choices = (
        (TASK_PAYMENT_METHOD_STRIPE, 'Stripe'),
        (TASK_PAYMENT_METHOD_BANK, 'Bank Transfer'),
        (TASK_PAYMENT_METHOD_BITCOIN, 'Bitcoin'),
        (TASK_PAYMENT_METHOD_BITONIC, 'Bitonic'),
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
        if self.invoice.type in [INVOICE_TYPE_CLIENT, INVOICE_TYPE_DEVELOPER]:
            return "sale"
        elif self.invoice.type == INVOICE_TYPE_TUNGA:
            return "purchase"

    def __str__(self):
        return "%s Amount: %s" % (self.invoice.project.title, self.amount)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.invoice:
            self.invoice.paid = True
            self.invoice.paid_at = datetime.datetime.now()
            self.invoice.save()
        super(Payment, self).save(force_insert, force_update, using, update_fields)

    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        if request.user == self.user or request.user == self.project.owner:
            return True
        elif request.user.is_project_manager and self.invoice.project.pm == request.user:
            return True
        elif request.user.is_project_manager and self.invoice.project.user == request.user:
            return True
        elif request.user.is_admin:
            return True
        elif request.user.is_developer and Participation.objects.filter(user=request.user, project=self.invoice.project,
                                                                        status=STATUS_ACCEPTED).count() > 0:
            return True
        else:
            return False

    @staticmethod
    @allow_staff_or_superuser
    def has_write_permission(self):
        return False

    @staticmethod
    @allow_staff_or_superuser
    def has_create_permission(self):
        return False

    @staticmethod
    @allow_staff_or_superuser
    def has_update_permission(self):
        return True

    @allow_staff_or_superuser
    def has_object_write_permission(self, request):
        return False

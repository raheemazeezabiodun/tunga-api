# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from dry_rest_permissions.generics import allow_staff_or_superuser

from tunga import settings
from tunga_projects.models import Project, Participation
from tunga_utils.constants import TASK_PAYMENT_METHOD_STRIPE, TASK_PAYMENT_METHOD_BANK, TASK_PAYMENT_METHOD_BITCOIN, \
    TASK_PAYMENT_METHOD_BITONIC, INVOICE_TYPE_TUNGA, STATUS_CANCELED, STATUS_APPROVED, STATUS_PENDING, \
    INVOICE_TYPE_CHOICES, CURRENCY_EUR, CURRENCY_CHOICES_EUR_ONLY, \
    INVOICE_TYPE_PURCHASE, PAYMENT_TYPE_PURCHASE, PAYMENT_TYPE_SALE


@python_2_unicode_compatible
class Invoice(models.Model):
    status_choices = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_CANCELED, 'Canceled')

    )

    project = models.ForeignKey(to=Project, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=200, null=True, blank=True)
    type = models.CharField(max_length=50, choices=INVOICE_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=17, decimal_places=2)
    currency = models.CharField(max_length=15, choices=CURRENCY_CHOICES_EUR_ONLY, default=CURRENCY_EUR)
    due_at = models.DateTimeField(default=datetime.datetime.utcnow)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    number = models.CharField(max_length=100, blank=True, null=True)
    processing_fee = models.DecimalField(max_digits=17, decimal_places=2, default=0)
    status = models.CharField(max_length=50, choices=status_choices, null=True, blank=True)
    paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    batch_ref = models.UUIDField(default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL, related_name='invoices_created', on_delete=models.DO_NOTHING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} | {}".format(self.title, self.user.get_full_name())

    class Meta:
        ordering = ['-due_at', '-created_at']

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.title:
            self.title = self.project.title
        if not self.status:
            if self.user.is_project_owner:
                self.status = STATUS_APPROVED
            elif self.user.is_developer:
                self.status = STATUS_PENDING
        if self.id and not self.number:
            self.number = self.generate_invoice_number()
        if self.paid and not self.paid_at:
            self.paid_at = datetime.datetime.utcnow()
        super(Invoice, self).save(force_insert, force_update, using, update_fields)

    @property
    def tax_amount(self):
        return (self.amount * self.tax_rate) / 100

    def generate_invoice_number(self):
        if self.id and not self.number:
            invoice_number = '{}/{}/P{}/{}'.format(
                (self.created_at or datetime.datetime.utcnow()).strftime('%Y'),
                self.project.owner and self.project.owner.id or self.project.user.id, self.project.id,
                self.id
            )
            if self.type == INVOICE_TYPE_PURCHASE:
                invoice_number = '{}/{}'.format(invoice_number, self.user.id)
            return invoice_number
        return self.number

    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return self.project.is_participant(request.user, active=True)

    @staticmethod
    @allow_staff_or_superuser
    def has_write_permission(request):
        return False

    @staticmethod
    @allow_staff_or_superuser
    def has_create_permission(request):
        return False

    @staticmethod
    @allow_staff_or_superuser
    def has_update_permission(request):
        return True

    @staticmethod
    @allow_staff_or_superuser
    def has_object_write_permission(self, request):
        return True


@python_2_unicode_compatible
class Payment(models.Model):
    payment_method_choices = (
        (TASK_PAYMENT_METHOD_STRIPE, 'Stripe'),
        (TASK_PAYMENT_METHOD_BANK, 'Bank Transfer'),
        (TASK_PAYMENT_METHOD_BITCOIN, 'Bitcoin'),
        (TASK_PAYMENT_METHOD_BITONIC, 'Bitonic'),
    )
    invoice = models.ForeignKey(to=Invoice, on_delete=models.DO_NOTHING)
    amount = models.IntegerField()
    currency = models.CharField(max_length=15, default='EUR')
    payment_method = models.CharField(max_length=150, choices=payment_method_choices)
    paid_at = models.DateTimeField(blank=True)
    created_by = models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='payments_created',
                                   on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s Amount: %s" % (self.invoice.project.title, self.amount)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.invoice:
            self.invoice.paid = True
            self.invoice.paid_at = datetime.datetime.now()
            self.invoice.save()
        super(Payment, self).save(force_insert, force_update, using, update_fields)

    @property
    def type(self):
        if self.invoice.type in [INVOICE_TYPE_TUNGA, INVOICE_TYPE_PURCHASE]:
            return PAYMENT_TYPE_PURCHASE
        else:
            return PAYMENT_TYPE_SALE

    @staticmethod
    @allow_staff_or_superuser
    def has_read_permission(request):
        return True

    @allow_staff_or_superuser
    def has_object_read_permission(self, request):
        return self.invoice.has_object_read_permission(request)

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

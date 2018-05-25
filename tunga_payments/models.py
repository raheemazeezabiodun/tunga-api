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
    created_by = models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='invoice_created_by', on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)
    number = models.CharField(max_length=150)
    batch_ref = models.CharField(max_length=150, default=uuid.uuid4)
    tax_amount = models.IntegerField()
    paid = models.BooleanField(default=False)

    def __str__(self):
        return "%s Paid: %s" % (self.project.title, self.paid)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.
from dry_rest_permissions.generics import DRYObjectPermissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from tunga_payments.models import Invoice, Payment
from tunga_payments.serializers import InvoiceSerializer, PaymentSerializer


class InvoiceViewSet(ModelViewSet):
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all()
    permission_classes = [IsAuthenticated, DRYObjectPermissions]


class PaymentViewSet(ModelViewSet):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated, DRYObjectPermissions]

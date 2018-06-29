# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.
from dry_rest_permissions.generics import DRYPermissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from tunga_payments.filterbackends import InvoiceFilterBackend, PaymentFilterBackend
from tunga_payments.filters import InvoiceFilter, PaymentFilter
from tunga_payments.models import Invoice, Payment
from tunga_payments.serializers import InvoiceSerializer, PaymentSerializer
from tunga_utils.filterbackends import DEFAULT_FILTER_BACKENDS


class InvoiceViewSet(ModelViewSet):
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all().order_by('id')
    permission_classes = [IsAuthenticated, DRYPermissions]
    filter_class = InvoiceFilter
    filter_backends = DEFAULT_FILTER_BACKENDS + (InvoiceFilterBackend,)

    def get_serializer(self, *args, **kwargs):
        if "data" in kwargs:
            data = kwargs["data"]
            if isinstance(data, list):
                kwargs["many"] = True
        return super(InvoiceViewSet, self).get_serializer(*args, **kwargs)


class PaymentViewSet(ModelViewSet):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated, DRYPermissions]
    filter_class = PaymentFilter
    filter_backends = DEFAULT_FILTER_BACKENDS + (PaymentFilterBackend,)

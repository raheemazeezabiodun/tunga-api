# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.
import uuid

from dry_rest_permissions.generics import DRYPermissions
from rest_framework import status
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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

    @list_route(methods=['post'], permission_classes=[IsAuthenticated, DRYPermissions],
                url_path='bulk', url_name='bulk-create-invoices')
    def create_bulk_invoices(self, request, pk=None):
        group_batch_ref = uuid.uuid4()
        for list_invoices in request.data:
            print(request.data)
            serializer = InvoiceSerializer(data=list_invoices, context={'request': request})
            if serializer.is_valid():
                serializer.save(batch_ref=group_batch_ref)
        results = Invoice.objects.filter(batch_ref=group_batch_ref)
        output_serializer = InvoiceSerializer(results, many=True)
        data = output_serializer.data[:]
        return Response(data, status=status.HTTP_201_CREATED)


class PaymentViewSet(ModelViewSet):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated, DRYPermissions]
    filter_class = PaymentFilter
    filter_backends = DEFAULT_FILTER_BACKENDS + (PaymentFilterBackend,)

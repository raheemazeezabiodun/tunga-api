# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.
import json
import uuid

import datetime
from decimal import Decimal

from dry_rest_permissions.generics import DRYPermissions
from rest_framework import status
from rest_framework.decorators import list_route, detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from stripe import InvalidRequestError

from tunga_payments.filterbackends import InvoiceFilterBackend, PaymentFilterBackend
from tunga_payments.filters import InvoiceFilter, PaymentFilter
from tunga_payments.models import Invoice, Payment
from tunga_payments.serializers import InvoiceSerializer, PaymentSerializer, StripePaymentSerializer
from tunga_utils import stripe_utils
from tunga_utils.constants import PAYMENT_METHOD_STRIPE, CURRENCY_EUR
from tunga_utils.filterbackends import DEFAULT_FILTER_BACKENDS


class InvoiceViewSet(ModelViewSet):
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all()
    #permission_classes = [IsAuthenticated, DRYPermissions]
    filter_class = InvoiceFilter
    filter_backends = DEFAULT_FILTER_BACKENDS + (InvoiceFilterBackend,)

    @list_route(methods=['post'], permission_classes=[IsAuthenticated, DRYPermissions],
                url_path='bulk', url_name='bulk-create-invoices')
    def create_bulk_invoices(self, request):
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

    @detail_route(
        methods=['get', 'post'], url_path='pay/', url_name='pay-invoice',
        serializer_class=StripePaymentSerializer,
        permission_classes=[IsAuthenticated]
    )
    def pay(self, request, pk=None, provider=None):
        """
            Invoice Payment Endpoint
            ---
            omit_serializer: true
            omit_parameters:
                - query
            """
        invoice = self.get_object()

        if provider == PAYMENT_METHOD_STRIPE:
            # Pay with Stripe
            payload = request.data
            paid_at = datetime.datetime.utcnow()

            stripe = stripe_utils.get_client()

            try:
                # Create customer
                customer = stripe.Customer.create(**dict(source=payload['token'], email=payload['email']))

                # Create Charge
                charge = stripe.Charge.create(
                    idempotency_key=payload.get('idem_key', None),
                    **dict(
                        amount=payload['amount'],
                        description=payload.get('description', invoice.title),
                        currency=payload.get('currency', CURRENCY_EUR),
                        customer=customer.id,
                        metadata=dict(
                            invoice_id=invoice.id,
                            project_id=invoice.project.id
                        )
                    )
                )

                if charge.paid:
                    # Save payment details
                    Payment.objects.create(
                        invoice=invoice,
                        payment_method=PAYMENT_METHOD_STRIPE,
                        amount=Decimal(charge.amount) * Decimal(0.01),
                        currency=(charge.currency or CURRENCY_EUR).upper(),
                        ref=charge.id,
                        paid_at=paid_at,
                        extra=json.dumps(dict(
                            paid=charge.paid,
                            token=payload['token'],
                            email=payload['email'],
                            captured=charge.captured,
                        ))
                    )

                    # Update invoice
                    invoice.paid = True
                    invoice.paid_at = paid_at
                    invoice.save()

                invoice_serializer = InvoiceSerializer(invoice, context={'request': request})
                return Response(invoice_serializer.data)
            except InvalidRequestError:
                return Response(dict(message='We could not process your payment! Please contact hello@tunga.io'),
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(dict(message='We could not process your payment! Please contact hello@tunga.io'),
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentViewSet(ModelViewSet):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated, DRYPermissions]
    filter_class = PaymentFilter
    filter_backends = DEFAULT_FILTER_BACKENDS + (PaymentFilterBackend,)

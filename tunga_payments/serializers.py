import uuid

from rest_framework import serializers
from rest_framework.serializers import ListSerializer

from tunga_payments.models import Payment, Invoice
from tunga_utils.serializers import NestedModelSerializer, ContentTypeAnnotatedModelSerializer


class InvoiceListSerializer(ListSerializer):
    def create(self, validated_data):
        group_batch_ref = uuid.uuid4()
        invoices = [Invoice(batch_ref=group_batch_ref, **item) for item in validated_data]
        return Invoice.objects.bulk_create(invoices)


class InvoiceSerializer(NestedModelSerializer, ContentTypeAnnotatedModelSerializer):
    batch_ref = serializers.CharField(read_only=True)

    class Meta:
        model = Invoice
        fields = ('id', 'project', 'user', 'type', 'amount', 'currency', 'tax_rate',
                  'processing_fee', 'created_by', 'number', 'batch_ref', 'tax_amount', 'paid')
        list_serializer_class = InvoiceListSerializer


class PaymentSerializer(NestedModelSerializer, ContentTypeAnnotatedModelSerializer):
    class Meta:
        model = Payment
        fields = ('id', 'invoice', 'amount', 'currency', 'payment_method',
                  'created_by')

import uuid

from rest_framework import serializers
from rest_framework.serializers import ListSerializer

from tunga_payments.models import Payment, Invoice
from tunga_projects.serializers import SimpleProjectSerializer
from tunga_utils.serializers import NestedModelSerializer, ContentTypeAnnotatedModelSerializer, \
    CreateOnlyCurrentUserDefault, SimplestUserSerializer, SimpleModelSerializer


class SimpleInvoiceSerializer(SimpleModelSerializer):
    created_by = SimplestUserSerializer(required=False, read_only=True, default=CreateOnlyCurrentUserDefault())
    user = SimplestUserSerializer()

    class Meta:
        model = Invoice
        exclude = ('project',)


class InvoiceListSerializer(ListSerializer):

    def create(self, validated_data):
        group_batch_ref = uuid.uuid4()
        invoices = [Invoice(batch_ref=group_batch_ref, **item) for item in validated_data]
        return Invoice.objects.bulk_create(invoices)


class InvoiceSerializer(NestedModelSerializer, ContentTypeAnnotatedModelSerializer):
    created_by = SimplestUserSerializer(required=False, read_only=True, default=CreateOnlyCurrentUserDefault())
    project = SimpleProjectSerializer()
    user = SimplestUserSerializer()
    batch_ref = serializers.CharField(read_only=True)
    tax_amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = Invoice
        fields = '__all__'
        list_serializer_class = InvoiceListSerializer


class PaymentSerializer(NestedModelSerializer, ContentTypeAnnotatedModelSerializer):
    created_by = SimplestUserSerializer(required=False, read_only=True, default=CreateOnlyCurrentUserDefault())
    invoice = SimpleInvoiceSerializer()

    class Meta:
        model = Payment
        fields = '__all__'

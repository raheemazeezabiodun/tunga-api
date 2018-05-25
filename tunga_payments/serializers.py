from rest_framework.serializers import ModelSerializer

from tunga_payments.models import Payment, Invoice


class InvoiceSerializer(ModelSerializer):
    class Meta:
        model = Invoice
        fields = ('project', 'user', 'type', 'amount', 'currency', 'tax_rate',
                  'processing_fee', 'created_by', 'number', 'batch_ref')


class PaymentSerializer(ModelSerializer):
    class Meta:
        model = Payment
        fields = ('project', 'invoice', 'amount', 'currency', 'payment_method',
                  'created_by')

from tunga_payments.models import Invoice
from tunga_utils.filters import GenericDateFilterSet


class InvoiceFilter(GenericDateFilterSet):
    class Meta:
        model = Invoice
        fields = ('type', 'batch_ref', 'number', 'user', 'project', 'created_by', 'paid')

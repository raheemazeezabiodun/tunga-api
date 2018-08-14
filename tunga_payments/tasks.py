import datetime
from decimal import Decimal

from django_rq.decorators import job

from tunga.settings import PAYONEER_USERNAME, PAYONEER_PASSWORD, PAYONEER_PARTNER_ID
from tunga_payments.models import Payment, Invoice
from tunga_utils import payoneer_utils
from tunga_utils.constants import PAYMENT_METHOD_PAYONEER, CURRENCY_EUR, STATUS_APPROVED, INVOICE_TYPE_PURCHASE, \
    STATUS_FAILED, STATUS_RETRY, STATUS_INITIATED
from tunga_utils.helpers import clean_instance


@job
def make_payout(invoice):
    invoice = clean_instance(invoice, Invoice)

    if invoice.legacy_id:
        # No pay outs for legacy invoices
        return

    if invoice.type != INVOICE_TYPE_PURCHASE or invoice.status != STATUS_APPROVED or invoice.paid:
        # Only payout non-paid approved purchase invoices
        return

    payoneer_client = payoneer_utils.get_client(
        PAYONEER_USERNAME, PAYONEER_PASSWORD, PAYONEER_PARTNER_ID
    )

    balance = payoneer_client.get_balance()
    if Decimal(20) <= invoice.amount <= balance.get('accountbalance', 0):
        # Payments must be more than EUR 20 and less than the balance

        payment, created = Payment.objects.get_or_create(
            invoice=invoice, defaults=dict(
                amount=invoice.amount, payment_method=PAYMENT_METHOD_PAYONEER
            )
        )

        if created or (payment and payment.status == STATUS_RETRY):
            if payment.status == STATUS_RETRY:
                payment.status = STATUS_INITIATED
                payment.save()

            transaction = payoneer_client.make_payment(
                PAYONEER_PARTNER_ID, 'invoice{}'.format(invoice.id), invoice.user.id, invoice.amount,
                invoice.full_title
            )

            if transaction.get('status', None) == '000':
                paid_at = datetime.datetime.utcnow()

                # Update invoice
                invoice.paid = True
                invoice.paid_at = paid_at
                invoice.save()

                payment.invoice = invoice
                payment.amount = invoice.amount
                payment.payment_method = PAYMENT_METHOD_PAYONEER
                payment.currency = invoice.currency or CURRENCY_EUR
                payment.ref = transaction.get('paymentid', None)
                payment.paid_at = paid_at
                payment.created_by = invoice.created_by
                payment.save()
            else:
                payment.status = STATUS_FAILED
                payment.save()

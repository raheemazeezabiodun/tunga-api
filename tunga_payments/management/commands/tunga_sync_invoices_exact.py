import datetime

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand

from tunga_payments.models import Invoice
from tunga_utils.constants import INVOICE_TYPE_SALE, INVOICE_TYPE_PURCHASE
from tunga_utils.exact_utils import upload_invoice_v3


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Schedule progress updates and send update reminders
        """
        # command to run: python manage.py tunga_sync_invoices_exact

        today_start = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        past_by_48_hours = today_start - relativedelta(hours=48)

        invoices = Invoice.objects.filter(
            type__in=[INVOICE_TYPE_SALE, INVOICE_TYPE_PURCHASE], paid=True, legacy_id__isnull=True,
            paid_at__gte=past_by_48_hours
        )
        for invoice in invoices:
            upload_invoice_v3(invoice)

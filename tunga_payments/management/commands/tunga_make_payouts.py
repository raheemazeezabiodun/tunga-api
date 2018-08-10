from django.core.management.base import BaseCommand

from tunga_payments.models import Invoice
from tunga_payments.tasks import make_payout
from tunga_utils.constants import INVOICE_TYPE_PURCHASE


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Update periodic update events and send reminds for upcoming update events.
        """
        # command to run: python manage.py tunga_manage_project_progress_events

        invoices = Invoice.objects.filter(type=INVOICE_TYPE_PURCHASE, payment__isnull=True, legacy_id__isnull=True)
        for invoice in invoices:
            # Make pay out
            make_payout(invoice)

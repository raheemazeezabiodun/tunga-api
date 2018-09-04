import datetime

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand

from tunga_payments.models import Invoice
from tunga_projects.tasks import weekly_payment_report


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Schedule weekly projects reports and updates

        """
        right_now = datetime.datetime.utcnow()
        past_by_7_days = right_now - relativedelta(days=7)
        past_by_1_days = right_now - relativedelta(days=1)
        past_by_15_days = right_now - relativedelta(days=15)
        next_by_7_days = right_now + relativedelta(days=8)

        paid_invoices_last_week = Invoice.objects.filter(
            paid_at__range=[past_by_7_days, right_now],
            paid=True
        ).values_list('id', flat=True)
        paid_invoices_last_week = list(paid_invoices_last_week)

        unpaid_overdue_invoices = Invoice.objects.filter(
            paid=False,
            issued_at__lt=past_by_15_days
        ).values_list('id', flat=True)
        unpaid_overdue_invoices = list(unpaid_overdue_invoices)

        unpaid_invoices = Invoice.objects.filter(
            paid=False,
            issued_at__range=[past_by_1_days, next_by_7_days]
        ).values_list('id', flat=True)

        unpaid_invoices = list(unpaid_invoices)
        print "unpaid_invoices"
        print unpaid_invoices
        print "unpaid_overdue_invoices"
        print unpaid_overdue_invoices
        print "paid_invoices_last_week"
        print paid_invoices_last_week

        weekly_payment_report(paid=paid_invoices_last_week,
                              unpaid_overdue=unpaid_overdue_invoices,
                              unpaid=unpaid_invoices
                              )

import datetime

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand

from tunga_tasks.models import Task
from tunga_tasks.notifications.email import notify_new_task_invoice_client_email


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Invoice payment reminder.
        """
        # command to run: python manage.py tunga_invoice_reminder
        past_by_2_weeks = datetime.datetime.utcnow() - relativedelta(weeks=2)
        tasks = Task.objects.filter(
            paid=False,
            invoice_date__lt=past_by_2_weeks,
            payment_reminder_sent_at__isnull=True
        )

        for task in tasks:
            notify_new_task_invoice_client_email(
                task.invoice, template_name='70-invoice-reminder-1'
            )
            task.payment_reminder_sent_at = datetime.datetime.utcnow()
            task.save()

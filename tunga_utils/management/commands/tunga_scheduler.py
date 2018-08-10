from apscheduler.schedulers.blocking import BlockingScheduler
from django.core.management import call_command
from django.core.management.base import BaseCommand

scheduler = BlockingScheduler()


@scheduler.scheduled_job('interval', minutes=5)
def make_payouts():
    # Make payouts
    call_command('tunga_make_payouts')


@scheduler.scheduled_job('interval', days=1)
def manage_progress_updates():
    # Schedule progress updates and send update reminders
    call_command('tunga_manage_progress_updates')


@scheduler.scheduled_job('interval', minutes=10)
def send_message_emails():
    # Send new message emails for conversations
    call_command('tunga_send_message_emails')

    # Send new activity emails for tasks
    call_command('tunga_send_task_activity_emails')

    # Send new message emails for customer support conversations
    call_command('tunga_send_customer_emails')


@scheduler.scheduled_job('interval', days=1)
def invoice_reminder():
    # Send unpaid invoice reminders
    call_command('tunga_invoice_reminder')
    call_command('tunga_invoice_reminder_escalated')


@scheduler.scheduled_job('interval', days=1)
def exact_sync():
    # Sync invoices with exact
    call_command('tunga_exact_sync')


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Run tunga periodic (cron) tasks.
        """
        # command to run: python manage.py tunga_scheduler

        scheduler.start()

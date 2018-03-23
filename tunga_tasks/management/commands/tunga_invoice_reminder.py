import datetime
from django.core.management.base import BaseCommand
from tunga_tasks.models import Task
from tunga_tasks.notifications.email import notify_new_task_invoice_admin_email, notify_new_task_invoice_client_email

class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Distribute task payments.
        """
        # command to run: python manage.py tunga_invoice_reminder
        reminder_day = 14        
        all_tasks = Task.objects.all().filter(paid=False)

        for tsk in all_tasks:
            if(tsk.is_due_date(reminder_day)):
                # Send a Email or slack.
                #notify_new_task_invoice_client_email(instance, recipient=None, reminder=False, client=False, reminder_template="")
                notify_new_task_invoice_client_email(tsk.invoice,
                                        reminder=True, client=True,
                                        reminder_template="70-invoice-reminder-1"
                                        )
            else:
                print "Not yet due date"


import datetime
from django.core.management.base import BaseCommand
from tunga_tasks.models import Task

class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Distribute task payments.
        """
        # command to run: python manage.py tunga_invoice_reminder_3_weeks.py
        reminder_day = 21
        
        all_tasks = Task.objects.all().filter(paid=False)

        for tsk in all_tasks:
            if(tsk.is_due_date(reminder_day)):
                # Send a Email or slack.
                print("Sending notification email")
                return 
            else:
                print "Not yet due date"


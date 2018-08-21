import datetime

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand

from tunga_projects.models import ProgressEvent
from tunga_projects.notifications.generic import notify_missed_progress_event


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Schedule progress updates and send update reminders
        """
        # command to run: python manage.py tunga_missed_progress_updates

        right_now = datetime.datetime.utcnow()
        past_by_18_hours = right_now - relativedelta(hours=18)
        past_by_48_hours = right_now - relativedelta(hours=48)

        # Notify Tunga of missed updates (limit to events due in last 48 hours, prevents spam from very old projects)
        missed_events = ProgressEvent.objects.filter(
            project__archived=False,
            due_at__range=[past_by_48_hours, past_by_18_hours],
            last_reminder_at__isnull=False,
            missed_notification_at__isnull=True
        )

        for event in missed_events:
            notify_missed_progress_event(event.id)

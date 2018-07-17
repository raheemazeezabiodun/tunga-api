import datetime

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand

from tunga_tasks.notifications.generic import send_survey_summary_report
from tunga_tasks.models import ProgressEvent, ProgressReport
from tunga_utils.constants import LEGACY_PROGRESS_EVENT_TYPE_CLIENT, LEGACY_PROGRESS_EVENT_TYPE_PM, LEGACY_PROGRESS_EVENT_TYPE_PERIODIC, \
    LEGACY_PROGRESS_EVENT_TYPE_DEFAULT, LEGACY_PROGRESS_EVENT_TYPE_COMPLETE, LEGACY_PROGRESS_EVENT_TYPE_SUBMIT, \
    LEGACY_PROGRESS_EVENT_TYPE_MILESTONE_INTERNAL, LEGACY_PROGRESS_EVENT_TYPE_CLIENT_MID_SPRINT


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Update periodic update events and send notifications for upcoming update events.
        """
        # command to run: python manage.py tunga_send_summary_reports

        right_now = datetime.datetime.utcnow()

        last_thursday = right_now - relativedelta(days=right_now.weekday()) + relativedelta(days=3, weeks=-1)
        last_sunday = last_thursday + relativedelta(days=3)

        if right_now.weekday() < 2:
            # Runs starting Wednesday
            return

        # Send reminders for tasks updates due in the current 24 hr period
        events = ProgressEvent.objects.filter(
            type__in=[LEGACY_PROGRESS_EVENT_TYPE_CLIENT, LEGACY_PROGRESS_EVENT_TYPE_CLIENT_MID_SPRINT],
            due_at__range=[last_sunday, right_now]
        )
        for event in events:
            print('\n\n')
            print(event)

            try:
                client_report = ProgressReport.objects.filter(
                    event=event, event__type__in=[LEGACY_PROGRESS_EVENT_TYPE_CLIENT, LEGACY_PROGRESS_EVENT_TYPE_CLIENT_MID_SPRINT],
                    event__due_at__range=[last_sunday, right_now]
                ).latest('event__due_at')
            except:
                client_report = None

            try:
                pm_report = ProgressReport.objects.filter(
                    event__task=event.task, event__type__in=[
                        LEGACY_PROGRESS_EVENT_TYPE_PM, LEGACY_PROGRESS_EVENT_TYPE_MILESTONE_INTERNAL
                    ],
                    event__due_at__range=[last_thursday, right_now]
                ).latest('event__due_at')
            except:
                pm_report = None

            try:
                dev_report = ProgressReport.objects.filter(
                    event__task=event.task,
                    event__type__in=[
                        LEGACY_PROGRESS_EVENT_TYPE_PERIODIC,
                        LEGACY_PROGRESS_EVENT_TYPE_DEFAULT,
                        LEGACY_PROGRESS_EVENT_TYPE_SUBMIT,
                        LEGACY_PROGRESS_EVENT_TYPE_COMPLETE
                    ],
                    event__due_at__range=[last_thursday, right_now]
                ).latest('event__due_at')
            except:
                dev_report = None

            print('client reports: ', client_report)
            print('pm report: ', pm_report)
            print('dev report: ', dev_report)

            send_survey_summary_report(event, client_report, pm_report, dev_report)

from django.core.management.base import BaseCommand

from tunga_projects.notifications.slack import notify_weekly_project_report_slack, notify_weekly_payment_report_slack


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Schedule progress updates and send update reminders
        """
        # command to run: python manage.py tunga_manage_weekly_reports

        notify_weekly_project_report_slack.delay()

        notify_weekly_payment_report_slack.delay()

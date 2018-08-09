from django_rq import job

from tunga_projects.notifications.email import notify_new_participant_email_dev, \
    notify_new_progress_report_email_client, notify_new_invoice_email_client
from tunga_projects.notifications.slack import notify_new_project_slack_admin, notify_new_progress_report_slack, \
    notify_new_invoice_slack_admin


@job
def notify_new_project(project):
    notify_new_project_slack_admin(project)


@job
def notify_new_participant(participation):
    notify_new_participant_email_dev(participation)


@job
def notify_new_progress_report(progress_report):
    notify_new_progress_report_email_client(progress_report)
    notify_new_progress_report_slack(progress_report, updated=False)


@job
def notify_new_invoice(invoice):
    notify_new_invoice_email_client(invoice)
    notify_new_invoice_slack_admin(invoice)

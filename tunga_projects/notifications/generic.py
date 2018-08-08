from django_rq import job

from tunga_projects.notifications.email import notify_new_participant_email_dev
from tunga_projects.notifications.slack import notify_new_project_slack_admin


@job
def notify_new_project(project):
    notify_new_project_slack_admin(project)


@job
def notify_new_participant(instance):
    notify_new_participant_email_dev(instance)

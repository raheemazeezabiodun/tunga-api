from django_rq import job

from tunga_projects.notifications.slack import notify_new_project_slack_admin


@job
def notify_new_project(instance):
    notify_new_project_slack_admin(instance)

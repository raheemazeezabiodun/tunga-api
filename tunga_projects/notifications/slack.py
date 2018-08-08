from django.template.defaultfilters import floatformat, truncatewords
from django_rq import job

from tunga.settings import TUNGA_URL, SLACK_STAFF_INCOMING_WEBHOOK, SLACK_STAFF_LEADS_CHANNEL, \
    SLACK_ATTACHMENT_COLOR_TUNGA, SLACK_ATTACHMENT_COLOR_GREEN
from tunga_projects.models import Project
from tunga_utils import slack_utils
from tunga_utils.helpers import clean_instance


@job
def notify_new_project_slack_admin(project):
    project = clean_instance(project, Project)
    project_url = '{}/projects/{}/'.format(TUNGA_URL, project.id)

    summary = "New project created by {} | <{}|View on Tunga>".format(
        project.user.display_name.encode('utf-8'),
        project_url
    )

    attachments = [
        {
            slack_utils.KEY_TITLE: project.title,
            slack_utils.KEY_TITLE_LINK: project_url,
            slack_utils.KEY_TEXT: project.description or project.title,
            slack_utils.KEY_MRKDWN_IN: [slack_utils.KEY_TEXT],
            slack_utils.KEY_COLOR: SLACK_ATTACHMENT_COLOR_TUNGA
        }
    ]

    extra_details = ''
    if project.type:
        extra_details += '*Type*: {}\n'.format(project.get_type_display())
    if project.expected_duration:
        extra_details += '*Expected duration*: {}\n'.format(project.get_expected_duration_display())
    if project.skills:
        extra_details += '*Skills*: {}\n'.format(str(project.skills))
    if project.deadline:
        extra_details += '*Deadline*: {}\n'.format(project.deadline.strftime("%d %b, %Y"))
    if project.budget:
        extra_details += '*Fee*: EUR {}\n'.format(floatformat(project.budget, arg=-2))

    if extra_details:
        attachments.append({
            slack_utils.KEY_TEXT: extra_details,
            slack_utils.KEY_MRKDWN_IN: [slack_utils.KEY_TEXT],
            slack_utils.KEY_COLOR: SLACK_ATTACHMENT_COLOR_GREEN
        })

    slack_utils.send_incoming_webhook(SLACK_STAFF_INCOMING_WEBHOOK, {
        slack_utils.KEY_TEXT: summary,
        slack_utils.KEY_CHANNEL: SLACK_STAFF_LEADS_CHANNEL,
        slack_utils.KEY_ATTACHMENTS: attachments
    })

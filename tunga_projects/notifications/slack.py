from django.template.defaultfilters import floatformat, truncatewords
from django_rq import job

from tunga.settings import TUNGA_URL, SLACK_STAFF_INCOMING_WEBHOOK, SLACK_STAFF_LEADS_CHANNEL, \
    SLACK_ATTACHMENT_COLOR_TUNGA, SLACK_ATTACHMENT_COLOR_GREEN
from tunga_projects.models import Project
from tunga_utils import slack_utils
from tunga_utils.helpers import clean_instance


@job
def notify_new_project_slack_admin(instance):
    instance = clean_instance(instance, Project)
    project_url = '{}/projects/{}/'.format(TUNGA_URL, instance.id)

    summary = "New project created by {} | <{}|View on Tunga>".format(
        instance.user.display_name.encode('utf-8'),
        project_url
    )

    attachments = [
        {
            slack_utils.KEY_TITLE: instance.title,
            slack_utils.KEY_TITLE_LINK: project_url,
            slack_utils.KEY_TEXT: instance.description or instance.title,
            slack_utils.KEY_MRKDWN_IN: [slack_utils.KEY_TEXT],
            slack_utils.KEY_COLOR: SLACK_ATTACHMENT_COLOR_TUNGA
        }
    ]

    extra_details = ''
    if instance.type:
        extra_details += '*Type*: {}\n'.format(instance.get_type_display())
    if instance.expected_duration:
        extra_details += '*Expected duration*: {}\n'.format(instance.get_type_display())
    if instance.skills:
        extra_details += '*Skills*: {}\n'.format(instance.skills_list)
    if instance.deadline:
        extra_details += '*Deadline*: {}\n'.format(instance.deadline.strftime("%d %b, %Y"))
    if instance.budget:
        amount = instance.budget
        extra_details += '*Fee*: EUR {}\n'.format(floatformat(amount, arg=-2))

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

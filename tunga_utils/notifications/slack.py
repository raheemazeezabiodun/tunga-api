from django_rq.decorators import job

from tunga.settings import SLACK_STAFF_INCOMING_WEBHOOK, SLACK_STAFF_PROFILES_CHANNEL, SLACK_ATTACHMENT_COLOR_GREEN
from tunga_utils import slack_utils
from tunga_utils.helpers import clean_instance
from tunga_utils.models import InviteRequest


@job
def notify_new_invite_request_slack(invite_request):
    invite_request = clean_instance(invite_request, InviteRequest)

    slack_msg = "@domieck {} wants to join Tunga".format(
        invite_request.name
    )

    attachments = [
        {
            slack_utils.KEY_TITLE: invite_request.name,
            slack_utils.KEY_TITLE_LINK: invite_request.cv_url,
            slack_utils.KEY_TEXT: '*Name:* {}\n*Email:* {}\n*Country*: {}\n<{}|Download CV>'.format(
                invite_request.name,
                invite_request.email,
                invite_request.country.name,
                invite_request.cv_url
            ),
            slack_utils.KEY_MRKDWN_IN: [slack_utils.KEY_TEXT],
            slack_utils.KEY_COLOR: SLACK_ATTACHMENT_COLOR_GREEN,
        }
    ]

    slack_utils.send_incoming_webhook(
        SLACK_STAFF_INCOMING_WEBHOOK,
        {
            slack_utils.KEY_TEXT: slack_msg,
            slack_utils.KEY_ATTACHMENTS: attachments,
            slack_utils.KEY_CHANNEL: SLACK_STAFF_PROFILES_CHANNEL
        }
    )


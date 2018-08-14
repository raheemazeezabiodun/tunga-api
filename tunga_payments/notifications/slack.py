from django_rq import job

from tunga.settings import TUNGA_URL, SLACK_ATTACHMENT_COLOR_BLUE, SLACK_STAFF_INCOMING_WEBHOOK, \
    SLACK_STAFF_PAYMENTS_CHANNEL
from tunga_payments.models import Invoice
from tunga_utils import slack_utils
from tunga_utils.constants import INVOICE_TYPE_SALE
from tunga_utils.helpers import clean_instance


@job
def notify_new_invoice_slack_admin(invoice):
    invoice = clean_instance(invoice, Invoice)

    if invoice.legacy_id:
        # ignore legacy invoices
        return

    project_url = '{}/projects/{}/'.format(TUNGA_URL, invoice.project.id)
    payment_url = '{}/pay'.format(project_url)
    person_url = '{}/network/{}/'.format(TUNGA_URL, invoice.user.username)
    invoice_url = '{}/api/invoices/{}/download/?format=pdf'.format(TUNGA_URL, invoice.id)
    slack_msg = '{} generated a {} invoice'.format(
        invoice.created_by.display_name.encode('utf-8'),
        invoice.type == INVOICE_TYPE_SALE and 'client' or 'developer'
    )

    invoice_summary = '{}: <{}|{}>\nProject: <{}|{}>\nTitle: {}\nFee: EUR {}\n<{}|Download invoice>'.format(
        invoice.type == INVOICE_TYPE_SALE and 'Client' or 'Developer',
        person_url, invoice.user.display_name.encode('utf-8'),
        project_url, invoice.project.title,
        invoice.title,
        invoice.amount,
        invoice_url
    )

    attachments = [
        {
            slack_utils.KEY_TITLE: invoice.title,
            slack_utils.KEY_TITLE_LINK: payment_url,
            slack_utils.KEY_TEXT: invoice_summary,
            slack_utils.KEY_MRKDWN_IN: [slack_utils.KEY_TEXT],
            slack_utils.KEY_COLOR: SLACK_ATTACHMENT_COLOR_BLUE
        },
    ]

    slack_utils.send_incoming_webhook(
        SLACK_STAFF_INCOMING_WEBHOOK,
        {
            slack_utils.KEY_TEXT: slack_msg,
            slack_utils.KEY_ATTACHMENTS: attachments,
            slack_utils.KEY_CHANNEL: SLACK_STAFF_PAYMENTS_CHANNEL
        }
    )

from django_rq import job

from tunga_payments.notifications.email import notify_new_invoice_email_client
from tunga_payments.notifications.slack import notify_new_invoice_slack_admin


@job
def notify_new_invoice(invoice):
    notify_new_invoice_email_client(invoice)
    notify_new_invoice_slack_admin(invoice)

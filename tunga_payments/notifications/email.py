import base64

from django_rq import job

from tunga.settings import TUNGA_URL, MANDRILL_VAR_FIRST_NAME
from tunga_payments.models import Invoice
from tunga_utils import mandrill_utils
from tunga_utils.constants import INVOICE_TYPE_SALE
from tunga_utils.helpers import clean_instance


@job
def notify_new_invoice_email_client(invoice):
    invoice = clean_instance(invoice, Invoice)

    if invoice.legacy_id:
        # ignore legacy invoices
        return

    if invoice.type != INVOICE_TYPE_SALE:
        # Only notify about client invoices
        return

    to = [invoice.user.email]
    if invoice.project.owner and invoice.project.owner.email != invoice.user.email:
        to.append(invoice.project.owner.email)

    if invoice.project.user and invoice.project.user.email != invoice.user.email:
        to.append(invoice.project.user.email)

    payment_link = '{}/projects/{}/pay'.format(TUNGA_URL, invoice.project.id)

    merge_vars = [
        mandrill_utils.create_merge_var(MANDRILL_VAR_FIRST_NAME, invoice.user.first_name),
        mandrill_utils.create_merge_var('project_title', '{}: {}'.format(invoice.project.title, invoice.title)),
        mandrill_utils.create_merge_var('payment_link', payment_link),
    ]

    pdf_file_contents = base64.b64encode(invoice.pdf)

    attachments = [
        dict(
            content=pdf_file_contents,
            name='Invoice - {}.pdf'.format(invoice.title),
            type='application/pdf'
        )
    ]

    mandrill_utils.send_email('83-invoice-email', to, merge_vars=merge_vars, attachments=attachments)

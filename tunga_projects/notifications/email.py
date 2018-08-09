import base64

from django_rq import job

from tunga.settings import TUNGA_URL, MANDRILL_VAR_FIRST_NAME
from tunga_payments.models import Invoice
from tunga_projects.models import Participation, ProgressReport
from tunga_settings.slugs import NEW_TASK_PROGRESS_REPORT_EMAIL
from tunga_settings.utils import check_switch_setting
from tunga_utils import mandrill_utils
from tunga_utils.constants import PROGRESS_EVENT_MILESTONE, \
    PROGRESS_EVENT_DEVELOPER, INVOICE_TYPE_SALE
from tunga_utils.emails import send_mail
from tunga_utils.helpers import clean_instance


@job
def notify_new_participant_email_dev(participation):
    participation = clean_instance(participation, Participation)

    subject = "Project invitation from {}".format(participation.created_by.first_name)
    to = [participation.user.email]
    ctx = {
        'inviter': participation.created_by,
        'invitee': participation.user,
        'project': participation.project,
        'project_url': '{}/projects/{}/'.format(TUNGA_URL, participation.project.id)
    }
    send_mail(
        subject, 'tunga/email/project_invitation', to, ctx
    )


@job
def notify_new_progress_report_email_client(progress_report):
    progress_report = clean_instance(progress_report, ProgressReport)

    is_dev_report = progress_report.event.type == PROGRESS_EVENT_DEVELOPER or \
                    (progress_report.event.type == PROGRESS_EVENT_MILESTONE and progress_report.user.is_developer)

    if not is_dev_report:
        # Only dev reports are sent by email to clients
        return

    subject = "{} submitted a Progress Report".format(
        progress_report.user.display_name.encode('utf-8')
    )

    to = []
    if is_dev_report:
        if progress_report.event.project.owner and check_switch_setting(progress_report.event.project.owner, NEW_TASK_PROGRESS_REPORT_EMAIL):
            to.append(progress_report.event.project.owner.email)
        elif progress_report.event.project.user and check_switch_setting(progress_report.event.project.user, NEW_TASK_PROGRESS_REPORT_EMAIL):
            to.append(progress_report.event.project.user.email)
        # TODO: Re-enable admins
        # admins = progress_report.event.project.admins
        # if admins:
        #    to.extend([user.email for user in admins])

    if not to:
        # Should have some recipients
        return

    ctx = {
        'owner': progress_report.event.project.owner or progress_report.event.project.user,
        'reporter': progress_report.user,
        'event': progress_report.event,
        'report': progress_report,
        'update_url': '{}/projects/{}/events/{}/'.format(TUNGA_URL, progress_report.event.project.id, progress_report.event.id)
    }

    send_mail(
        subject, 'tunga/email/new_progress_report', to, ctx
    )


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

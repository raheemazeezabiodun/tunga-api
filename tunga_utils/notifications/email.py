import datetime

from django_rq.decorators import job

from tunga.settings import TUNGA_CONTACT_REQUEST_EMAIL_RECIPIENTS
from tunga_utils import mandrill_utils
from tunga_utils.emails import send_mail
from tunga_utils.helpers import clean_instance
from tunga_utils.models import ContactRequest


@job
def notify_new_contact_request_email(contact_request):
    contact_request = clean_instance(contact_request, ContactRequest)

    if contact_request.body:
        merge_vars = [
            mandrill_utils.create_merge_var('full_name', contact_request.fullname),
            mandrill_utils.create_merge_var('email', contact_request.email),
            mandrill_utils.create_merge_var('message', contact_request.body),
        ]

        mandrill_utils.send_email(
            '73_Platform-guest-emails',
            TUNGA_CONTACT_REQUEST_EMAIL_RECIPIENTS,
            merge_vars=merge_vars
        )
    else:
        subject = "New {} Request".format(contact_request.item and 'Offer' or 'Contact')
        msg_suffix = 'wants to know more about Tunga.'
        if contact_request.item:
            item_name = contact_request.get_item_display()
            subject = '%s (%s)' % (subject, item_name)
            msg_suffix = 'requested for "%s"' % item_name
        to = TUNGA_CONTACT_REQUEST_EMAIL_RECIPIENTS

        ctx = {
            'email': contact_request.email,
            'message': '%s %s ' % (
                contact_request.email,
                msg_suffix
            )
        }

        if send_mail(subject, 'tunga/email/contact_request_message', to, ctx):
            contact_request.email_sent_at = datetime.datetime.utcnow()
            contact_request.save()


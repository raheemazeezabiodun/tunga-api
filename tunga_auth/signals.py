from allauth.account.models import EmailAddress
from allauth.account.signals import user_signed_up
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from tunga_auth.models import EmailVisitor
from tunga_auth.notifications import send_new_user_joined_email, send_new_user_password_email
from tunga_auth.tasks import sync_hubspot_contact, sync_hubspot_email
from tunga_utils.constants import USER_TYPE_PROJECT_OWNER, USER_SOURCE_MANUAL


@receiver(post_save, sender=get_user_model())
def activity_handler_new_user(sender, instance, created, **kwargs):
    if created:
        if not EmailAddress.objects.filter(email=instance.email).count():
            email_address = EmailAddress.objects.add_email(
                None, instance, instance.email
            )

            if instance.is_admin:
                email_address.verified = True
                email_address.primary = True
                email_address.save()

        if instance.source == USER_SOURCE_MANUAL:
            send_new_user_password_email.delay(instance.id)


@receiver(user_signed_up)
def activity_handler_new_signup(request, user, **kwargs):
    send_new_user_joined_email.delay(user.id)

    if user.type == USER_TYPE_PROJECT_OWNER:
        sync_hubspot_contact.delay(user.id)


@receiver(post_save, sender=EmailVisitor)
def activity_handler_new_email_visitor(sender, instance, created, **kwargs):
    if created:
        sync_hubspot_email.delay(instance.email)

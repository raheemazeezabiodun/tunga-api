from actstream.signals import action
from django.contrib.admin.options import get_content_type_for_model
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver, Signal

from tunga_activity import verbs
from tunga_messages.models import Channel
from tunga_tasks.models import Task
from tunga_utils.models import ContactRequest, Upload, InviteRequest
from tunga_utils.notifications.generic import notify_new_contact_request, notify_new_invite_request


post_nested_save = Signal(providing_args=["instance", "created"])
post_field_update = Signal(providing_args=["instance", "field"])


@receiver(post_save, sender=ContactRequest)
def activity_handler_new_contact_request(sender, instance, created, **kwargs):
    if created:
        notify_new_contact_request.delay(instance.id)


@receiver(post_save, sender=Upload)
def activity_handler_new_upload(sender, instance, created, **kwargs):
    if created and instance.content_type in [get_content_type_for_model(Channel), get_content_type_for_model(Task)]:
        action.send(instance.user, verb=verbs.UPLOAD, action_object=instance, target=instance.content_object)


@receiver(post_save, sender=InviteRequest)
def activity_handler_new_invite_request(sender, instance, created, **kwargs):
    if created:
        notify_new_invite_request.delay(instance.id)

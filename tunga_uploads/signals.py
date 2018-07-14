from actstream.signals import action
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from tunga_activity import verbs
from tunga_uploads.models import Upload


@receiver(post_save, sender=Upload)
def activity_handler_upload(sender, instance, created, **kwargs):
    if created:
        action.send(instance.user, verb=verbs.UPLOAD, action_object=instance, target=instance.content_object)

from actstream import action
from django.db.models.signals import post_save
from django.dispatch import receiver

from tunga_activity import verbs
from tunga_activity.models import FieldChangeLog


@receiver(post_save, sender=FieldChangeLog)
def activity_handler_new_field_change(sender, instance, created, **kwargs):
    if created:
        action.send(instance.created_by, verb=verbs.CREATE, action_object=instance, target=instance.content_object)

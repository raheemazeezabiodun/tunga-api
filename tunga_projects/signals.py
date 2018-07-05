from actstream import action
from django.db.models.signals import post_save
from django.dispatch import receiver

from tunga_activity import verbs
from tunga_projects.models import Project, Participation, Document, ProgressEvent


@receiver(post_save, sender=Project)
def activity_handler_new_task(sender, instance, created, **kwargs):
    if created:
        action.send(instance.user, verb=verbs.CREATE, action_object=instance)


@receiver(post_save, sender=Participation)
def activity_handler_new_task(sender, instance, created, **kwargs):
    if created:
        action.send(instance.created_by, verb=verbs.CREATE, action_object=instance)


@receiver(post_save, sender=Document)
def activity_handler_new_task(sender, instance, created, **kwargs):
    if created:
        action.send(instance.created_by, verb=verbs.CREATE, action_object=instance)


@receiver(post_save, sender=ProgressEvent)
def activity_handler_new_task(sender, instance, created, **kwargs):
    if created:
        action.send(instance.created_by, verb=verbs.CREATE, action_object=instance)

from actstream import action
from django.db.models.signals import post_save
from django.dispatch import receiver

from tunga_activity import verbs
from tunga_projects.models import Project, Participation, Document, ProgressEvent, ProgressReport
from tunga_projects.notifications.generic import notify_new_project, notify_new_participant, notify_new_progress_report
from tunga_projects.notifications.slack import notify_new_progress_report_slack


@receiver(post_save, sender=Project)
def activity_handler_new_project(sender, instance, created, **kwargs):
    if created:
        action.send(instance.user, verb=verbs.CREATE, action_object=instance)

        if not instance.legacy_id:
            notify_new_project.delay(instance.id)


@receiver(post_save, sender=Participation)
def activity_handler_new_participation(sender, instance, created, **kwargs):
    if created and not instance.legacy_id:
        action.send(instance.created_by, verb=verbs.CREATE, action_object=instance, target=instance.project)

        notify_new_participant.delay(instance.id)


@receiver(post_save, sender=Document)
def activity_handler_new_document(sender, instance, created, **kwargs):
    if created and not instance.legacy_id:
        action.send(instance.created_by, verb=verbs.CREATE, action_object=instance, target=instance.project)


@receiver(post_save, sender=ProgressEvent)
def activity_handler_new_progress_event(sender, instance, created, **kwargs):
    if created and not instance.legacy_id:
        action.send(instance.created_by, verb=verbs.CREATE, action_object=instance, target=instance.project)


@receiver(post_save, sender=ProgressReport)
def activity_handler_new_progress_report(sender, instance, created, **kwargs):
    if created and not instance.legacy_id:
        action.send(instance.user, verb=verbs.CREATE, action_object=instance, target=instance.event)
        notify_new_progress_report.delay(instance.id)
    else:
        notify_new_progress_report_slack.delay(instance.id, updated=True)

from actstream import action
from django.db.models.signals import post_save
from django.dispatch import receiver

from tunga_activity import verbs
from tunga_payments.models import Invoice, Payment


@receiver(post_save, sender=Invoice)
def activity_handler_new_invoice(sender, instance, created, **kwargs):
    if created:
        action.send(instance.created_by, verb=verbs.CREATE, action_object=instance)


@receiver(post_save, sender=Payment)
def activity_handler_new_payment(sender, instance, created, **kwargs):
    if created:
        action.send(instance.created_by, verb=verbs.CREATE, action_object=instance)

from actstream import action
from django.db.models.signals import post_save
from django.dispatch import receiver

from tunga_activity import verbs
from tunga_payments.models import Invoice, Payment


@receiver(post_save, sender=Invoice)
def activity_handler_new_invoice(sender, instance, created, **kwargs):
    if created:
        if not instance.legacy_id:
            action.send(instance.created_by, verb=verbs.CREATE, action_object=instance, target=instance.project)

        # save again to generate invoice number
        instance.save()


@receiver(post_save, sender=Payment)
def activity_handler_new_payment(sender, instance, created, **kwargs):
    if created and not instance.legacy_id:
        action.send(instance.created_by, verb=verbs.CREATE, action_object=instance, target=instance.invoice)

import datetime
import uuid

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from tunga_payments.models import Invoice
from tunga_payments.serializers import SimpleInvoiceSerializer
from tunga_projects.models import Project
from tunga_tasks.models import Task, ParticipantPayment
from tunga_utils.constants import STATUS_APPROVED, STATUS_ACCEPTED, INVOICE_TYPE_PURCHASE


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Migrate dev invoices
        """
        # command to run: python manage.py tunga_migrate_invoices_client

        tasks = Task.objects.all()
        for task in tasks:
            legacy_invoice = task.invoice

            if legacy_invoice:

                if legacy_invoice.version < 2:
                    print('no v1 and pre-v1 imports yet', legacy_invoice.id, legacy_invoice.task.id,
                          legacy_invoice.task.summary)
                    continue

                print('task invoice: ', legacy_invoice.id, legacy_invoice.task.id, legacy_invoice.task.summary)

                target_task = task
                if task.parent:
                    target_task = task.parent

                try:
                    project = Project.objects.get(legacy_id=target_task.id)
                except ObjectDoesNotExist:
                    project = None

                if project:
                    # Project must exist
                    print('project: ', project.id, project.title)

                    field_map = [
                        ['title', 'title'],
                        ['currency', 'currency'],
                        ['payment_method', 'payment_method'],
                        ['btc_address', 'btc_address'],
                    ]

                    participation_shares = task.get_participation_shares()
                    group_batch_ref = uuid.uuid4()

                    for share_info in participation_shares:
                        participant = share_info['participant']
                        dev = participant.user

                        if participant.status != STATUS_ACCEPTED or share_info['share'] <= 0:
                            continue

                        payments = ParticipantPayment.objects.filter(participant=participant)

                        if payments:
                            payment = payments[0]
                            legacy_invoice_id = '{}_{}'.format(legacy_invoice.id, dev.id)

                            try:
                                v3_invoice = Invoice.objects.get(legacy_id=legacy_invoice_id)
                            except ObjectDoesNotExist:
                                v3_invoice = Invoice()

                            v3_invoice.legacy_id = legacy_invoice_id
                            v3_invoice.user = dev
                            v3_invoice.project = project
                            v3_invoice.type = INVOICE_TYPE_PURCHASE
                            v3_invoice.status = STATUS_APPROVED
                            v3_invoice.due_at = legacy_invoice.created_at
                            v3_invoice.number = legacy_invoice.invoice_id(invoice_type='tunga', user=dev)

                            for item in field_map:
                                field_value = getattr(legacy_invoice, item[1], None)
                                if field_value:
                                    setattr(v3_invoice, item[0], field_value)

                            amount_details = legacy_invoice.get_amount_details(share=share_info['share'])

                            v3_invoice.amount = amount_details.get('invoice_tunga', 0)
                            v3_invoice.processing_fee = amount_details.get('processing', 0)
                            v3_invoice.tax_rate = 0
                            v3_invoice.created_by = legacy_invoice.user or legacy_invoice.task.user
                            v3_invoice.paid = True
                            v3_invoice.paid_at = payment.sent_at or payment.created_at
                            v3_invoice.batch_ref = group_batch_ref

                            print('total_invoice_tunga: ', amount_details.get('total_invoice_tunga', 0))

                            if not v3_invoice.migrated_at:
                                v3_invoice.migrated_at = datetime.datetime.utcnow()

                            print('v3_invoice: ', SimpleInvoiceSerializer(instance=v3_invoice).data)
                            v3_invoice.save()

                            v3_invoice.created_at = legacy_invoice.created_at
                            v3_invoice.tax_rate = 0
                            v3_invoice.batch_ref = group_batch_ref
                            v3_invoice.save()
                            print('new invoice', v3_invoice.id, v3_invoice.project.id, v3_invoice.amount)
                else:
                    print('project not migrated', legacy_invoice.task.id)

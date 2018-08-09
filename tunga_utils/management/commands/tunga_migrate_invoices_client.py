import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from tunga_payments.models import Invoice
from tunga_payments.serializers import SimpleInvoiceSerializer
from tunga_projects.models import Project
from tunga_tasks.models import Task
from tunga_utils.constants import INVOICE_TYPE_SALE, STATUS_APPROVED


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Migrate invoices
        """
        # command to run: python manage.py tunga_migrate_invoices

        tasks = Task.objects.all()
        for task in tasks:
            legacy_invoice = task.invoice

            if legacy_invoice:

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

                    legacy_invoice_id = '{}_{}'.format(legacy_invoice.id, legacy_invoice.client.id)

                    try:
                        v3_invoice = Invoice.objects.get(legacy_id=legacy_invoice_id)
                    except ObjectDoesNotExist:
                        v3_invoice = Invoice()
                    v3_invoice.legacy_id = legacy_invoice_id
                    v3_invoice.user = legacy_invoice.client
                    v3_invoice.project = project
                    v3_invoice.type = INVOICE_TYPE_SALE
                    v3_invoice.status = STATUS_APPROVED
                    v3_invoice.due_at = legacy_invoice.created_at
                    v3_invoice.number = legacy_invoice.invoice_id(invoice_type='client', user=legacy_invoice.client)

                    for item in field_map:
                        field_value = getattr(legacy_invoice, item[1], None)
                        if field_value:
                            setattr(v3_invoice, item[0], field_value)

                    v3_invoice.amount = legacy_invoice.amount.get('invoice_client', 0)
                    v3_invoice.processing_fee = legacy_invoice.amount.get('processing', 0)
                    v3_invoice.tax_rate = legacy_invoice.tax_rate
                    v3_invoice.created_by = legacy_invoice.user or legacy_invoice.task.user
                    v3_invoice.paid = legacy_invoice.task.paid
                    v3_invoice.paid_at = legacy_invoice.task.paid_at

                    print('client_total_plus_tax: ', legacy_invoice.amount.get('total_invoice_client_plus_tax', 0))

                    if not v3_invoice.migrated_at:
                        v3_invoice.migrated_at = datetime.datetime.utcnow()

                    print('v3_invoice: ', SimpleInvoiceSerializer(instance=v3_invoice).data)
                    v3_invoice.save()

                    v3_invoice.created_at = legacy_invoice.created_at
                    v3_invoice.tax_rate = legacy_invoice.tax_rate
                    v3_invoice.save()
                    print('new invoice', v3_invoice.id, v3_invoice.project.id, v3_invoice.amount)
                else:
                    print('project not migrated', legacy_invoice.task.id)

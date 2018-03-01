# -*- coding: utf-8 -*-

from copy import copy

from django.db.models.query_utils import Q
from django.template.loader import render_to_string
from django_rq.decorators import job
from weasyprint import HTML

from tunga_profiles.models import DeveloperNumber
from tunga_tasks.models import Task
from tunga_utils import bitcoin_utils
from tunga_utils.constants import TASK_PAYMENT_METHOD_BITCOIN
from tunga_utils.serializers import InvoiceUserSerializer, TaskInvoiceSerializer


@job
def process_invoices(pk, invoice_types=('client',), user_id=None, developer_ids=None, is_admin=False, filepath=None):
    """
    :param pk: id of the task
    :param invoice_types: tuple of invoice types to generate e.g 'client', 'developer', 'tunga'
    :param user_id: user viewing the invoice(s)
    :param developer_ids: participant invoices to generate. only applies to 'developer' and 'tunga' invoices
    :param is_admin: is requester an admin?
    :param filepath: file to store invoice in
    :return:
    """
    all_invoices = list()

    if pk == 'all':
        tasks = Task.objects.filter(closed=True, taskinvoice__isnull=False)
        if user_id and not is_admin:
            tasks = tasks.filter(
                Q(user_id=user_id) | Q(owner_id=user_id) | Q(pm_id=user_id) | Q(participant__user_id=user_id))
        tasks = tasks.distinct()
    else:
        tasks = Task.objects.filter(id=pk)

    for task in tasks:
        invoice = task.invoice
        if invoice:
            invoice = invoice.clean_invoice()
            if invoice.number:
                initial_invoice_data = TaskInvoiceSerializer(invoice).data
                initial_invoice_data['date'] = task.invoice.created_at.strftime('%d %B %Y')

                task_owner = task.user
                if task.owner:
                    task_owner = task.owner

                participation_shares = task.get_participation_shares()
                common_developer_info = list()
                for share_info in participation_shares:
                    participant = share_info['participant']
                    developer, created = DeveloperNumber.objects.get_or_create(user=participant.user)

                    amount_details = invoice.get_amount_details(share=share_info['share'])

                    if (not developer_ids or participant.user.id in developer_ids) and \
                            not (participant.prepaid or (participant.prepaid is None and participant.user.is_internal)):
                        common_developer_info.append({
                            'developer': InvoiceUserSerializer(participant.user).data,
                            'amount': amount_details,
                            'dev_number': developer.number or '',
                            'participant': participant
                        })

                for invoice_type in invoice_types:
                    if invoice_type == 'developer' and invoice.version > 1:
                        continue
                    task_developers = []
                    invoice_data = copy(initial_invoice_data)

                    if invoice_type == 'client':
                        invoice_data['number_client'] = invoice.invoice_id(invoice_type='client')
                        task_developers = [dict()]
                    else:
                        for common_info in common_developer_info:
                            final_dev_info = copy(common_info)
                            final_dev_info['number'] = invoice.invoice_id(
                                invoice_type=invoice_type,
                                user=common_info['participant'] and common_info['participant'].user or None
                            )

                            participant_payment_method = None
                            if common_info['participant']:
                                try:
                                    participant_payment = common_info['participant'].participantpayment_set.filter().latest('created_at')
                                    if participant_payment and bitcoin_utils.is_valid_btc_address(participant_payment.destination):
                                        participant_payment_method = TASK_PAYMENT_METHOD_BITCOIN
                                except:
                                    pass

                            final_dev_info['payment_method'] = participant_payment_method
                            task_developers.append(final_dev_info)

                    invoice_data['developers'] = task_developers

                    client_country = None
                    if invoice_type == 'client' and task_owner.profile and \
                            task_owner.profile.country and task_owner.profile.country.code:
                        client_country = task_owner.profile.country.code

                    if client_country == 'NL':
                        invoice_location = 'NL'
                    elif client_country in [
                        # EU members
                        'BE', 'BG', 'CZ', 'DK', 'DE', 'EE', 'IE', 'EL', 'ES', 'FR', 'HR', 'IT', 'CY', 'LV', 'LT', 'LU',
                        'HU', 'MT', 'AT', 'PL', 'PT', 'RO', 'SI', 'SK', 'FI', 'SE', 'UK'
                        # European Free Trade Association (EFTA)
                        'IS', 'LI', 'NO', 'CH'
                    ]:
                        invoice_location = 'europe'
                    else:
                        invoice_location = 'world'

                    all_invoices.append(
                        dict(
                            invoice_type=invoice_type,
                            invoice=invoice_data, location=invoice_location
                        )
                    )
    ctx = dict(
        invoices=all_invoices
    )

    rendered_html = render_to_string("tunga/pdf/invoice.html", context=ctx).encode(encoding="UTF-8")
    if filepath:
        HTML(string=rendered_html, encoding='utf-8').write_pdf(filepath)
    return rendered_html

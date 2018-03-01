import base64

from exactonline.api import ExactApi
from exactonline.exceptions import ObjectDoesNotExist
from exactonline.resource import POST
from exactonline.storage import IniStorage

from tunga.settings import BASE_DIR, EXACT_DOCUMENT_TYPE_PURCHASE_INVOICE, EXACT_DOCUMENT_TYPE_SALES_INVOICE
from tunga_profiles.models import DeveloperNumber


def get_api():
    storage = IniStorage(BASE_DIR + '/tunga/exact.ini')
    return ExactApi(storage=storage)


def upload_invoice(task, user, invoice_type, invoice_file):
    """
    :param task: parent task for the invoice
    :param user: Tunga user related to the invoice e.g a client or a developer
    :param invoice_type: type of invoice e.g 'client', 'developer', 'tunga'
    :param invoice_file: generated file object for the invoice
    :return:
    """
    exact_api = get_api()
    invoice = task.invoice

    exact_user_id = None
    try:
        exact_user_id = exact_api.relations.get(relation_code=user.exact_code)['ID']
    except (ObjectDoesNotExist, TypeError):
        pass

    relation_dict = dict(
        Code=user.exact_code,
        Name=user.display_name,
        Email=user.email,
        City=user.profile and user.profile.city_name or '',
        Country=user.profile and user.profile.country.code or ''
    )

    if invoice_type == 'tunga':
        relation_dict['IsSupplier'] = True
    else:
        relation_dict['IsSales'] = True

    if exact_user_id:
        exact_api.relations.update(exact_user_id, relation_dict)
    else:
        exact_user = exact_api.relations.create(relation_dict)
        exact_user_id = exact_user['ID']

    invoice_number = invoice.invoice_id(invoice_type=invoice_type, user=user)

    invoice_dict = dict(
        Type=invoice_type == 'tunga' and EXACT_DOCUMENT_TYPE_PURCHASE_INVOICE or EXACT_DOCUMENT_TYPE_SALES_INVOICE,
        Subject='{} - {}'.format(
            invoice.title,
            invoice_number
        ),
        Account=exact_user_id,
    )
    exact_document = exact_api.restv1(POST('documents/Documents', invoice_dict))

    attachment_dict = dict(
        Attachment=base64.b64encode(invoice_file),
        Document=exact_document['ID'],
        FileName='{} - {}.pdf'.format(invoice.title, invoice_number)
    )
    exact_api.restv1(POST('documents/DocumentAttachments', attachment_dict))


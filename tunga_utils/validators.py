import datetime
import re

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from tunga.settings import UPLOAD_SIZE_LIMIT_MBS
from tunga_utils.bitcoin_utils import is_valid_btc_address


def validate_email(value):
    if get_user_model().objects.filter(email__iexact=value).count():
        raise ValidationError('This email is already associated with a Tunga account')


def validate_year(value):
    this_year = datetime.date.today().year
    min_year = this_year - 80
    if value < min_year:
        raise ValidationError('Year should be after %s' % min_year)
    if value > this_year:
        raise ValidationError('Year should not be after %s' % this_year)


def validate_btc_address(value):
    error_msg = 'Invalid Bitcoin address.'
    if re.match(r"[a-zA-Z1-9]{27,35}$", value) is None:
        raise ValidationError(error_msg)
    if not is_valid_btc_address(value):
        raise ValidationError(error_msg)


def validate_btc_address_or_none(value):
    error_msg = 'Invalid Bitcoin address.'
    if value is not None and re.match(r"[a-zA-Z1-9]{27,35}$", value) is None:
        raise ValidationError(error_msg)
    if value is not None and not is_valid_btc_address(value):
        raise ValidationError(error_msg)


def validate_file_size(value):
    if value.size > UPLOAD_SIZE_LIMIT_MBS:
        raise ValidationError('File is too large, uploads must not exceed 5 MB.')


def validate_field_schema(required_fields_schema, data, raise_exception=True):
    """
    Validate required data based on schema
    :param required_fields_schema:
    :param data:
    :param raise_exception:
    :return:
    """
    # TODO: Document validation schema format
    errors = dict()

    for field_item in required_fields_schema:
        if type(field_item) in [tuple, list]:
            field_name = field_item[0]
            field_value = data.get(field_name, None)
            field_validator = len(field_item) > 1 and field_item[1] or None
            is_validation_field_value = (type(field_validator) in [tuple, list] and field_value in field_validator) or \
                                        (type(field_validator) not in [tuple, list] and field_value is not None)

            if not is_validation_field_value:
                errors[field_name] = field_value is None and 'This field is required.' or 'Invalid value "{}"'.format(field_value)

            if len(field_item) > 2:
                conditional_field_items = field_item[2]
                if type(conditional_field_items) in [tuple, list]:
                    for conditional_field_item in conditional_field_items:

                        if type(conditional_field_item) in [tuple, list]:
                            conditional_field_validator = conditional_field_item[0]
                            if (conditional_field_validator is None and not is_validation_field_value) or \
                                (type(conditional_field_validator) in [tuple, list] and field_value in conditional_field_validator) or \
                                (conditional_field_validator is not None and conditional_field_validator == field_value):
                                final_conditional_field_item = list(conditional_field_item)[1:]
                                errors.update(validate_field_schema([final_conditional_field_item], data, raise_exception=False))
                        else:
                            errors.update(validate_field_schema([conditional_field_item], data, raise_exception=False))
                else:
                    errors.update(validate_field_schema([conditional_field_items], data, raise_exception=False))

        else:
            if not data.get(field_item, None):
                errors[field_item] = 'This field is required.'
    if errors and raise_exception:
        raise ValidationError(errors)
    return errors

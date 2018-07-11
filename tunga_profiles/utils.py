from django.contrib.auth import get_user_model

from tunga_profiles.models import AppIntegration
from tunga_utils.constants import STATUS_APPROVED, STATUS_PENDING
from tunga_utils.helpers import clean_instance


def profile_check(user):
    user = clean_instance(user, get_user_model())
    if not user.first_name or not user.last_name or not user.email or not user.profile:
        return False

    if user.is_developer and user.payoneer_status not in [STATUS_APPROVED, STATUS_PENDING]:
        return False

    required = ['country', 'city', 'street', 'plot_number', 'postal_code']

    if user.is_developer or user.is_project_manager:
        required.extend(['id_document'])
    elif user.is_project_owner and user.tax_location == 'europe':
        required.extend(['vat_number'])

    profile_dict = user.profile.__dict__
    for key in profile_dict:
        if key in required and not profile_dict[key]:
            return False
    return True


def get_app_integration(user, provider):
    try:
        return AppIntegration.objects.filter(user=user, provider=provider).latest('updated_at')
    except AppIntegration.DoesNotExist:
        return None

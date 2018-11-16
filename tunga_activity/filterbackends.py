import datetime

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from dry_rest_permissions.generics import DRYPermissionFiltersBase

from tunga_payments.models import Invoice
from tunga_utils.filterbackends import dont_filter_staff_or_superuser


class ActivityFilterBackend(DRYPermissionFiltersBase):
    @dont_filter_staff_or_superuser
    def filter_list_queryset(self, request, queryset, view):
        if request.user and request.user.is_authenticated and not (request.user.is_admin or request.user.is_project_manager or request.user.is_developer):
            # Only Admins, PMs and Devs can view future invoices
            today_end = datetime.datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
            invoice_type = ContentType.objects.get_for_model(Invoice)
            queryset = queryset.filter(
                ~Q(action_object_content_type=invoice_type) | (
                    Q(action_object_content_type=ContentType.objects.get_for_model(Invoice)) &
                    Q(invoices__issued_at__lte=today_end)
                )
            )
        return queryset

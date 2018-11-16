import datetime
from django.db.models import Q
from dry_rest_permissions.generics import DRYPermissionFiltersBase

from tunga_utils.filterbackends import dont_filter_staff_or_superuser


class InvoiceFilterBackend(DRYPermissionFiltersBase):
    @dont_filter_staff_or_superuser
    def filter_list_queryset(self, request, queryset, view):
        if request.user and request.user.is_authenticated and not (request.user.is_admin or request.user.is_project_manager or request.user.is_developer):
            # Only Admins, PMs and Devs can view future invoices
            today_end = datetime.datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
            queryset = queryset.filter(issued_at__lte=today_end)
        return queryset.filter(
            Q(user=request.user) |
            Q(created_by=request.user) |
            Q(project__user=request.user) |
            Q(project__pm=request.user) |
            Q(project__owner=request.user)
        )


class PaymentFilterBackend(DRYPermissionFiltersBase):
    @dont_filter_staff_or_superuser
    def filter_list_queryset(self, request, queryset, view):
        return queryset.filter(
            Q(created_by=request.user) |
            Q(invoice__user=request.user) |
            Q(invoice__project__user=request.user) |
            Q(invoice__project__pm=request.user) |
            Q(invoice__project__owner=request.user)
        )

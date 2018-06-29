from django.db.models import Q
from dry_rest_permissions.generics import DRYPermissionFiltersBase

from tunga_utils.constants import STATUS_INITIAL, STATUS_ACCEPTED
from tunga_utils.filterbackends import dont_filter_staff_or_superuser


class InvoiceFilterBackend(DRYPermissionFiltersBase):
    @dont_filter_staff_or_superuser
    def filter_list_queryset(self, request, queryset, view):
        return queryset.filter(
            Q(user=request.user) |
            Q(project__user=request.user) |
            Q(pm__user=request.user) |
            Q(owner__user=request.user) |
            (
                Q(task__participation__user=request.user) &
                Q(task__participation__status__in=[STATUS_INITIAL, STATUS_ACCEPTED])
            )

        )


class PaymentFilterBackend(DRYPermissionFiltersBase):
    @dont_filter_staff_or_superuser
    def filter_list_queryset(self, request, queryset, view):
        return queryset.filter(
            Q(user=request.user) |
            Q(project__user=request.user) |
            Q(pm__user=request.user) |
            Q(owner__user=request.user) |
            (
                Q(task__participation__user=request.user) &
                Q(task__participation__status__in=[STATUS_INITIAL, STATUS_ACCEPTED])
            )

        )

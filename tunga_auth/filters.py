import django_filters
from django.contrib.auth import get_user_model
from django.db.models import Q

from tunga_utils.constants import USER_TYPE_DEVELOPER, USER_TYPE_PROJECT_OWNER, USER_TYPE_PROJECT_MANAGER
from tunga_utils.filters import NumberInFilter


class UserFilter(django_filters.FilterSet):
    skill = django_filters.CharFilter(name='userprofile__skills__name', label='skills')
    skill_id = django_filters.NumberFilter(name='userprofile__skills', label='skills (by ID)')
    types = NumberInFilter(name='type', lookup_expr='in', label='types')
    account_type = django_filters.CharFilter(method='filter_account_type')

    class Meta:
        model = get_user_model()
        fields = ('type', 'skill', 'skill_id', 'types', 'payoneer_status')

    def filter_account_type(self, queryset, name, value):
        type_map = dict(
            developer=USER_TYPE_DEVELOPER,
            project_owner=USER_TYPE_PROJECT_OWNER,
            project_manager=USER_TYPE_PROJECT_MANAGER,
            admin=USER_TYPE_PROJECT_OWNER
        )

        if value:
            if value in type_map:
                queryset = queryset.filter(type=type_map[value])
            if value == 'admin':
                queryset = queryset.filter(Q(is_staff=True) | Q(is_superuser=True))
        return queryset

import django_filters
from django.db.models import Q

from tunga_projects.models import Project, Document, Participation, ProgressEvent, ProgressReport
from tunga_utils.filters import GenericDateFilterSet


class ProjectFilter(GenericDateFilterSet):
    participant = django_filters.NumberFilter(name='participants__user', label='Participant')
    skill = django_filters.CharFilter(name='skills__name', label='skills')
    skill_id = django_filters.NumberFilter(name='skills', label='skills (by ID)')
    owner = django_filters.CharFilter(method='filter_owner')

    class Meta:
        model = Project
        fields = (
            'user', 'type', 'expected_duration', 'participant', 'skill', 'skill_id'
        )

    def filter_owner(self, queryset, name, value):
        return queryset.filter(Q(owner=value) | Q(user=value))


class ParticipationFilter(GenericDateFilterSet):

    class Meta:
        model = Participation
        fields = (
            'project', 'created_by'
        )


class DocumentFilter(GenericDateFilterSet):

    class Meta:
        model = Document
        fields = (
            'project', 'created_by'
        )


class ProgressEventFilter(GenericDateFilterSet):

    class Meta:
        model = ProgressEvent
        fields = (
            'project', 'created_by'
        )


class ProgressReportFilter(GenericDateFilterSet):

    class Meta:
        model = ProgressReport
        fields = (
            'event', 'user'
        )

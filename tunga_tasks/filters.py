# -*- coding: utf-8 -*-

import django_filters
from django.db.models.query_utils import Q

from tunga_tasks.models import Task, Application, Participation, TimeEntry, Project, ProgressReport, ProgressEvent, \
    Estimate, Quote, TaskPayment, ParticipantPayment, SkillsApproval, Sprint, TaskDocument
from tunga_utils.constants import PAYMENT_METHOD_STRIPE
from tunga_utils.filters import GenericDateFilterSet


class ProjectFilter(GenericDateFilterSet):

    class Meta:
        model = Project
        fields = ('user', 'closed')


class TaskFilter(GenericDateFilterSet):
    applicant = django_filters.NumberFilter(name='applications__user', label='Applicant')
    participant = django_filters.NumberFilter(name='participants__user', label='Participant')
    payment_status = django_filters.CharFilter(method='filter_payment_status')
    skill = django_filters.CharFilter(name='skills__name', label='skills')
    skill_id = django_filters.NumberFilter(name='skills', label='skills (by ID)')
    owner = django_filters.CharFilter(method='filter_owner')

    class Meta:
        model = Task
        fields = (
            'user', 'project', 'parent', 'type', 'scope', 'source', 'closed', 'applicant', 'participant',
            'paid', 'pay_distributed', 'payment_status',
            'skill', 'skill_id'
        )

    def filter_owner(self, queryset, name, value):
        return queryset.filter(Q(owner=value) | Q(user=value))

    def filter_payment_status(self, queryset, name, value):
        queryset = queryset.filter(closed=True)
        if value in ['paid', 'processing']:
            request = self.request
            is_admin = request and request.user and request.user.is_authenticated() and request.user.is_admin
            is_po = request and request.user and request.user.is_authenticated() and request.user.is_project_owner and not is_admin
            is_dev = request and request.user and request.user.is_authenticated() and request.user.is_developer and not is_admin
            is_pm = request and request.user and request.user.is_authenticated() and request.user.is_project_manager and not is_admin
            is_dev_or_pm = is_dev or is_pm
            paid_filter = Q(paid=True)
            if value == 'paid':
                if is_admin:
                    paid_filter = Q(paid=True) & Q(pay_distributed=True)
                elif is_dev_or_pm:
                    paid_filter = Q(pay_distributed=True)
                return queryset.filter(paid_filter)
            else:
                # exclude all paid work
                queryset = queryset.exclude(paid_filter)
                processing_filter = Q(processing=True) | Q(paid=True)
                if not is_po:
                    processing_filter = processing_filter | Q(paid=True)
                if is_dev_or_pm:
                    processing_filter = (processing_filter | Q(payment_approved=True)) & Q(pay_distributed=False)
                return queryset.filter(processing_filter)
        elif value == 'pending':
            queryset = queryset.filter(processing=False, paid=False)
        elif value == 'distribute':
            queryset = queryset.filter(
                payment_method=PAYMENT_METHOD_STRIPE,
                paid=True, btc_paid=False, pay_distributed=False
            )
        return queryset


class ApplicationFilter(GenericDateFilterSet):
    class Meta:
        model = Application
        fields = ('user', 'task', 'status')


class ParticipationFilter(GenericDateFilterSet):
    class Meta:
        model = Participation
        fields = ('user', 'task', 'status')


class EstimateFilter(GenericDateFilterSet):

    class Meta:
        model = Estimate
        fields = ('user', 'task', 'status', 'moderated_by')


class QuoteFilter(GenericDateFilterSet):

    class Meta:
        model = Quote
        fields = ('user', 'task', 'status', 'moderated_by')


class SprintFilter(GenericDateFilterSet):

    class Meta:
        model = Sprint
        fields = ('user', 'task', 'status', 'moderated_by')


class TimeEntryFilter(GenericDateFilterSet):
    min_date = django_filters.IsoDateTimeFilter(name='spent_at', lookup_expr='gte')
    max_date = django_filters.IsoDateTimeFilter(name='spent_at', lookup_expr='lte')
    min_hours = django_filters.IsoDateTimeFilter(name='hours', lookup_expr='gte')
    max_hours = django_filters.IsoDateTimeFilter(name='hours', lookup_expr='lte')

    class Meta:
        model = TimeEntry
        fields = ('user', 'task', 'spent_at', 'hours')


class ProgressEventFilter(GenericDateFilterSet):

    class Meta:
        model = ProgressEvent
        fields = ('created_by', 'task', 'type')


class ProgressReportFilter(GenericDateFilterSet):
    task = django_filters.NumberFilter(name='event__task')
    event_type = django_filters.NumberFilter(name='event__type')

    class Meta:
        model = ProgressReport
        fields = ('user', 'event', 'task', 'event_type', 'status')


class TaskPaymentFilter(GenericDateFilterSet):
    user = django_filters.NumberFilter(name='task_user')
    owner = django_filters.NumberFilter(name='task_owner')

    class Meta:
        model = TaskPayment
        fields = ('task', 'ref', 'payment_type', 'btc_address', 'processed', 'paid', 'captured', 'user', 'owner')


class ParticipantPaymentFilter(GenericDateFilterSet):
    user = django_filters.NumberFilter(name='participant__user')
    task = django_filters.NumberFilter(name='source__task')

    class Meta:
        model = ParticipantPayment
        fields = ('participant', 'source', 'destination', 'ref', 'idem_key', 'status', 'user', 'task')


class SkillsApprovalFilter(GenericDateFilterSet):
    developer = django_filters.NumberFilter(name='participant__user')
    task = django_filters.NumberFilter(name='participant__task')
    event_type = django_filters.NumberFilter(name='event__type')

    class Meta:
        model = SkillsApproval
        fields = ('created_by', 'developer', 'task', 'participant', 'approved_with')


class TaskDocumentFilter(GenericDateFilterSet):

    class Meta:
        model = TaskDocument
        fields = ('task', 'created_by')

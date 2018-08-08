import django_filters
from actstream.models import Action
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from tunga_activity import verbs
from tunga_activity.models import FieldChangeLog
from tunga_comments.models import Comment
from tunga_messages.models import Channel, Message
from tunga_payments.models import Invoice
from tunga_projects.models import Project, ProgressEvent, ProgressReport, Participation, Document
from tunga_tasks.models import Task, ProgressEvent as LegacyProgressEvent, ProgressReport as LegacyProgressReport, \
    Participation as LegacyParticipation, TaskDocument
from tunga_utils.filters import GenericDateFilterSet
from tunga_utils.models import Upload


class ActionFilter(GenericDateFilterSet):
    user = django_filters.NumberFilter(method='filter_user')
    task = django_filters.NumberFilter(method='filter_task')
    since = django_filters.NumberFilter(name='id', lookup_expr='gt')
    project = django_filters.NumberFilter(method='filter_project')
    channel = django_filters.NumberFilter(method='filter_channel')

    class Meta:
        model = Action
        fields = (
            'verb', 'actor_content_type', 'actor_object_id', 'target_content_type', 'target_object_id',
            'action_object_content_type', 'action_object_object_id', 'since', 'project'
        )

    def filter_user(self, queryset, name, value):
        return queryset.filter(
            actor_content_type=ContentType.objects.get_for_model(get_user_model()), actor_object_id=value
        )

    def filter_task(self, queryset, name, value):
        return queryset.filter(
            target_content_type=ContentType.objects.get_for_model(Task), target_object_id=value
        )

    def filter_project(self, queryset, name, value):
        project = Project.objects.get(pk=value)
        if not project.is_participant(self.request.user, active=True):
            return queryset.none()
        queries = []
        if project.legacy_id:
            task = Task.objects.get(pk=project.legacy_id)
            queries.append(
                (
                    Q(tasks=task) | Q(legacy_progress_events__task=task)
                ) &
                Q(
                    action_object_content_type__in=[
                        ContentType.objects.get_for_model(model) for model in [
                            Comment, Upload, LegacyProgressEvent, LegacyProgressReport, LegacyParticipation,
                            TaskDocument
                        ]
                    ]
                )
            )
        queries.append((
                Q(projects=project) | Q(progress_events__project=project)
            ) &
            Q(
                action_object_content_type__in=[
                    ContentType.objects.get_for_model(model) for model in [
                        Comment, Upload, ProgressEvent, ProgressReport, Participation, Document, Invoice, FieldChangeLog
                    ]
                ]
            ))

        query = queries.pop()
        for item in queries:
            query |= item
        return queryset.filter(query)

    def filter_channel(self, queryset, name, value):
        channel = Channel.objects.get(pk=value)
        return queryset.filter(
            channels=channel,
            action_object_content_type__in=[
                ContentType.objects.get_for_model(model) for model in [
                    Message, Upload
                ]
            ]
        )


class MessageActivityFilter(ActionFilter):
    since = django_filters.NumberFilter(method='filter_since')

    def filter_since(self, queryset, name, value):
        return queryset.filter(
            id__gt=value, verb__in=[verbs.SEND, verbs.UPLOAD]
        )

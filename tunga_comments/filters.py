import django_filters
from django.contrib.contenttypes.models import ContentType

from tunga_comments.models import Comment
from tunga_projects.models import Project
from tunga_utils.filters import GenericDateFilterSet
from tunga_tasks.models import Task


class CommentFilter(GenericDateFilterSet):
    since = django_filters.NumberFilter(name='id', lookup_expr='gt')
    task = django_filters.NumberFilter(method='filter_task')
    project = django_filters.NumberFilter(method='filter_project')

    class Meta:
        model = Comment
        fields = ('user', 'content_type', 'object_id', 'since', 'task', 'project')

    def filter_task(self, queryset, name, value):
        task_content_type = ContentType.objects.get_for_model(Task)
        return queryset.filter(content_type=task_content_type.id, object_id=value)

    def filter_project(self, queryset, name, value):
        project_content_type = ContentType.objects.get_for_model(Project)
        return queryset.filter(content_type=project_content_type.id, object_id=value)

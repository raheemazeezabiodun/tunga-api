import django_filters
from django.contrib.contenttypes.models import ContentType

from tunga_projects.models import Project
from tunga_uploads.models import Upload
from tunga_utils.filters import GenericDateFilterSet


class UploadFilter(GenericDateFilterSet):
    project = django_filters.NumberFilter(method='filter_project')

    class Meta:
        model = Upload
        fields = ('user', 'content_type', 'object_id', 'project')

    def filter_project(self, queryset, name, value):
        project_content_type = ContentType.objects.get_for_model(Project)
        return queryset.filter(content_type=project_content_type.id, object_id=value)

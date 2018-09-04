from django.core.management.base import BaseCommand

from tunga_projects.models import Project
from tunga_projects.tasks import weekly_project_report
from tunga_utils.constants import PROJECT_STAGE_ACTIVE


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Schedule weekly projects reports and updates

        """
        active_projects = Project.objects.filter(
            stage=PROJECT_STAGE_ACTIVE,
            archived=False,
            closed=False).values_list('id', flat=True)

        active_projects = list(active_projects)

        weekly_project_report(projects=active_projects)

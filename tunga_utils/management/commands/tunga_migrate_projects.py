import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from tunga_projects.models import Project
from tunga_projects.serializers import SimpleProjectSerializer
from tunga_tasks.models import Task
from tunga_utils.constants import TASK_TYPE_WEB, PROJECT_TYPE_WEB, TASK_TYPE_MOBILE, \
    PROJECT_TYPE_MOBILE, TASK_TYPE_OTHER, PROJECT_TYPE_OTHER, TASK_SCOPE_TASK, PROJECT_DURATION_2_WEEKS, \
    TASK_SCOPE_PROJECT, PROJECT_DURATION_6_MONTHS, TASK_SCOPE_ONGOING, PROJECT_DURATION_PERMANENT


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Migrate tasks to projects
        """
        # command to run: python manage.py tunga_migrate_projects

        tasks = Task.objects.filter(parent__isnull=True)
        for task in tasks:
            print('task: ', task.id, task.summary)

            field_map = [
                ['title', 'summary'],
                ['description', 'description'],
                ['user', 'user'],
                ['owner', 'owner'],
                ['pm', 'pm'],
                ['budget', 'pay'],
                ['deadline', 'deadline'],
                ['client_survey_enabled', 'survey_client'],
                ['closed', 'closed'],
                ['closed_at', 'closed_at'],
                ['archived', 'archived'],
                ['archived_at', 'archived_at']
            ]

            str_field_map = [
                ['skills', 'skills'],
            ]

            type_map = {
                TASK_TYPE_WEB: PROJECT_TYPE_WEB,
                TASK_TYPE_MOBILE: PROJECT_TYPE_MOBILE,
                TASK_TYPE_OTHER: PROJECT_TYPE_OTHER,
            }

            scope_map = {
                TASK_SCOPE_TASK: PROJECT_DURATION_2_WEEKS,
                TASK_SCOPE_PROJECT: PROJECT_DURATION_6_MONTHS,
                TASK_SCOPE_ONGOING: PROJECT_DURATION_PERMANENT
            }

            try:
                project = Project.objects.get(legacy_id=task.id)
            except ObjectDoesNotExist:
                project = Project()
            project.legacy_id = task.id

            for item in field_map:
                field_value = getattr(task, item[1], None)
                if field_value:
                    setattr(project, item[0], field_value)

            for item in str_field_map:
                field_value = str(getattr(task, item[1], None))
                if field_value:
                    setattr(project, item[0], field_value)

            if task.type:
                setattr(project, 'type', type_map.get(task.type, None))

            if task.scope:
                setattr(project, 'expected_duration', scope_map.get(task.scope, None))

            if task.closed and not task.archived:
                project.archived = True

                if task.archived_at:
                    project.archived_at = task.archived_at

            if not project.migrated_at:
                project.migrated_at = datetime.datetime.utcnow()

            print('project: ', SimpleProjectSerializer(instance=project).data)
            project.save()

            project.created_at = task.created_at
            project.save()

import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from tunga_projects.models import Project, ProgressEvent as V3ProgressEvent
from tunga_projects.serializers import SimpleProgressEventSerializer
from tunga_tasks.models import ProgressEvent as LegacyProgressEvent
from tunga_utils.constants import LEGACY_PROGRESS_EVENT_TYPE_CLIENT, PROGRESS_EVENT_CLIENT, \
    LEGACY_PROGRESS_EVENT_TYPE_CLIENT_MID_SPRINT, LEGACY_PROGRESS_EVENT_TYPE_DEFAULT, PROGRESS_EVENT_DEVELOPER, \
    LEGACY_PROGRESS_EVENT_TYPE_PM, PROGRESS_EVENT_PM, LEGACY_PROGRESS_EVENT_TYPE_PERIODIC, PROGRESS_EVENT_MILESTONE, \
    LEGACY_PROGRESS_EVENT_TYPE_SUBMIT, LEGACY_PROGRESS_EVENT_TYPE_COMPLETE, LEGACY_PROGRESS_EVENT_TYPE_MILESTONE, \
    LEGACY_PROGRESS_EVENT_TYPE_MILESTONE_INTERNAL, PROGRESS_EVENT_INTERNAL


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Migrate progress events
        """
        # command to run: python manage.py tunga_migrate_progress_events

        legacy_progress_event_set = LegacyProgressEvent.objects.all()
        for legacy_progress_event in legacy_progress_event_set:
            print('progress_event: ', legacy_progress_event.id, legacy_progress_event.title, legacy_progress_event.task.id, legacy_progress_event.task.summary)

            try:
                project = Project.objects.get(legacy_id=legacy_progress_event.task.id)
            except ObjectDoesNotExist:
                project = None

            if project:
                # Project must exist
                print('project: ', project.id, project.title)

                field_map = [
                    ['due_at', 'due_at'],
                    ['title', 'title'],
                    ['description', 'description'],
                    ['last_reminder_at', 'last_reminder_at'],
                    ['missed_notification_at', 'missed_notification_at'],
                    ['created_by', 'created_by'],
                ]

                type_map = {
                    LEGACY_PROGRESS_EVENT_TYPE_DEFAULT: PROGRESS_EVENT_DEVELOPER,
                    LEGACY_PROGRESS_EVENT_TYPE_PERIODIC: PROGRESS_EVENT_DEVELOPER,
                    LEGACY_PROGRESS_EVENT_TYPE_CLIENT: PROGRESS_EVENT_CLIENT,
                    LEGACY_PROGRESS_EVENT_TYPE_CLIENT_MID_SPRINT: PROGRESS_EVENT_CLIENT,
                    LEGACY_PROGRESS_EVENT_TYPE_PM: PROGRESS_EVENT_PM,
                    LEGACY_PROGRESS_EVENT_TYPE_SUBMIT: PROGRESS_EVENT_MILESTONE,
                    LEGACY_PROGRESS_EVENT_TYPE_COMPLETE: PROGRESS_EVENT_MILESTONE,
                    LEGACY_PROGRESS_EVENT_TYPE_MILESTONE: PROGRESS_EVENT_MILESTONE,
                    LEGACY_PROGRESS_EVENT_TYPE_MILESTONE_INTERNAL: PROGRESS_EVENT_INTERNAL,
                }

                try:
                    v3_progress_event = V3ProgressEvent.objects.get(legacy_id=legacy_progress_event.id)
                except ObjectDoesNotExist:
                    v3_progress_event = V3ProgressEvent()
                v3_progress_event.legacy_id = legacy_progress_event.id
                v3_progress_event.project = project

                for item in field_map:
                    field_value = getattr(legacy_progress_event, item[1], None)
                    if field_value:
                        setattr(v3_progress_event, item[0], field_value)

                if legacy_progress_event.type:
                    setattr(v3_progress_event, 'type', type_map.get(legacy_progress_event.type, None))

                if not v3_progress_event.migrated_at:
                    v3_progress_event.migrated_at = datetime.datetime.utcnow()

                print('v3_progress_event: ', SimpleProgressEventSerializer(instance=v3_progress_event).data)
                v3_progress_event.save()

                v3_progress_event.created_at = legacy_progress_event.created_at
                v3_progress_event.save()
            else:
                print('project not migrated', legacy_progress_event.task.id)

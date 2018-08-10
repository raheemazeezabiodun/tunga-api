import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from tunga_projects.models import Project, Participation as V3Participation
from tunga_projects.serializers import SimpleParticipationSerializer
from tunga_tasks.models import Participation as LegacyParticipation


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Migrate participation
        """
        # command to run: python manage.py tunga_migrate_participation

        legacy_participation_set = LegacyParticipation.objects.all()
        for legacy_participation in legacy_participation_set:
            print('participation: ', legacy_participation.id, legacy_participation.user.display_name.encode('utf-8'))

            try:
                project = Project.objects.get(legacy_id=legacy_participation.task.id)
            except ObjectDoesNotExist:
                project = None

            if project:
                # Project must exist
                print('project: ', project.id, project.title)

                field_map = [
                    ['user', 'user'],
                    ['status', 'status'],
                    ['updates_enabled', 'updates_enabled'],
                    ['responded_at', 'activated_at'],
                    ['created_by', 'created_by'],
                ]

                try:
                    v3_participation = V3Participation.objects.get(legacy_id=legacy_participation.id)
                except ObjectDoesNotExist:
                    v3_participation = V3Participation()
                v3_participation.legacy_id = legacy_participation.id
                v3_participation.project = project

                for item in field_map:
                    field_value = getattr(legacy_participation, item[1], None)
                    if field_value:
                        setattr(v3_participation, item[0], field_value)

                if not v3_participation.migrated_at:
                    v3_participation.migrated_at = datetime.datetime.utcnow()

                print('v3_participation: ', SimpleParticipationSerializer(instance=v3_participation).data)
                v3_participation.save()

                v3_participation.created_at = legacy_participation.created_at
                v3_participation.updates_enabled = legacy_participation.updates_enabled
                v3_participation.save()
            else:
                print('project not migrated', legacy_participation.task.id)

import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from tunga_projects.models import ProgressEvent, ProgressReport as V3ProgressReport
from tunga_projects.serializers import SimpleProgressReportSerializer
from tunga_tasks.models import ProgressReport as LegacyProgressReport
from tunga_utils.constants import LEGACY_PROGRESS_REPORT_STATUS_ON_SCHEDULE, \
    LEGACY_PROGRESS_REPORT_STATUS_BEHIND, LEGACY_PROGRESS_REPORT_STATUS_STUCK, \
    LEGACY_PROGRESS_REPORT_STATUS_BEHIND_BUT_PROGRESSING, LEGACY_PROGRESS_REPORT_STATUS_BEHIND_AND_STUCK, \
    PROGRESS_REPORT_STATUS_ON_SCHEDULE, PROGRESS_REPORT_STATUS_BEHIND, PROGRESS_REPORT_STATUS_STUCK, \
    PROGRESS_REPORT_STATUS_BEHIND_BUT_PROGRESSING, PROGRESS_REPORT_STATUS_BEHIND_AND_STUCK, \
    LEGACY_PROGRESS_REPORT_STUCK_REASON_ERROR, PROGRESS_REPORT_STUCK_REASON_ERROR, \
    LEGACY_PROGRESS_REPORT_STUCK_REASON_POOR_DOC, PROGRESS_REPORT_STUCK_REASON_POOR_DOC, \
    LEGACY_PROGRESS_REPORT_STUCK_REASON_HARDWARE, PROGRESS_REPORT_STUCK_REASON_HARDWARE, \
    LEGACY_PROGRESS_REPORT_STUCK_REASON_UNCLEAR_SPEC, PROGRESS_REPORT_STUCK_REASON_UNCLEAR_SPEC, \
    LEGACY_PROGRESS_REPORT_STUCK_REASON_PERSONAL, PROGRESS_REPORT_STUCK_REASON_PERSONAL, \
    LEGACY_PROGRESS_REPORT_STUCK_REASON_OTHER, PROGRESS_REPORT_STUCK_REASON_OTHER


class Command(BaseCommand):

    def handle(self, *args, **options):
        """
        Migrate progress reports
        """
        # command to run: python manage.py tunga_migrate_progress_reports

        legacy_progress_report_set = LegacyProgressReport.objects.all()
        for legacy_progress_report in legacy_progress_report_set:
            print('progress_report: ', legacy_progress_report.id, legacy_progress_report.event.id, legacy_progress_report.event.type, legacy_progress_report.event.title)

            try:
                progress_event = ProgressEvent.objects.get(legacy_id=legacy_progress_report.event.id)
            except ObjectDoesNotExist:
                progress_event = None

            if progress_event:
                # Progress Event must exist
                print('progress_event: ', progress_event.id, progress_event.title)

                field_map = [
                    ['user', 'user'],
                    ['percentage', 'percentage'],
                    ['accomplished', 'accomplished'],
                    ['todo', 'todo'],
                    ['obstacles', 'obstacles'],
                    ['obstacles_prevention', 'obstacles_prevention'],
                    ['remarks', 'remarks'],
                    ['stuck_details', 'stuck_details'],
                    ['rate_deliverables', 'rate_deliverables'],
                    ['started_at', 'started_at'],
                    ['last_deadline_met', 'last_deadline_met'],
                    ['deadline_miss_communicated', 'deadline_miss_communicated'],
                    ['deadline_report', 'deadline_report'],
                    ['next_deadline', 'next_deadline'],
                    ['next_deadline_meet', 'next_deadline_meet'],
                    ['next_deadline_fail_reason', 'next_deadline_fail_reason'],
                    ['team_appraisal', 'team_appraisal'],
                    ['deliverable_satisfaction', 'deliverable_satisfaction'],
                    ['rate_communication', 'rate_communication'],
                    ['pm_communication', 'pm_communication'],
                ]

                status_map = {
                    LEGACY_PROGRESS_REPORT_STATUS_ON_SCHEDULE: PROGRESS_REPORT_STATUS_ON_SCHEDULE,
                    LEGACY_PROGRESS_REPORT_STATUS_BEHIND: PROGRESS_REPORT_STATUS_BEHIND,
                    LEGACY_PROGRESS_REPORT_STATUS_STUCK: PROGRESS_REPORT_STATUS_STUCK,
                    LEGACY_PROGRESS_REPORT_STATUS_BEHIND_BUT_PROGRESSING: PROGRESS_REPORT_STATUS_BEHIND_BUT_PROGRESSING,
                    LEGACY_PROGRESS_REPORT_STATUS_BEHIND_AND_STUCK: PROGRESS_REPORT_STATUS_BEHIND_AND_STUCK,
                }

                stuck_reason_map = {
                    LEGACY_PROGRESS_REPORT_STUCK_REASON_ERROR: PROGRESS_REPORT_STUCK_REASON_ERROR,
                    LEGACY_PROGRESS_REPORT_STUCK_REASON_POOR_DOC: PROGRESS_REPORT_STUCK_REASON_POOR_DOC,
                    LEGACY_PROGRESS_REPORT_STUCK_REASON_HARDWARE: PROGRESS_REPORT_STUCK_REASON_HARDWARE,
                    LEGACY_PROGRESS_REPORT_STUCK_REASON_UNCLEAR_SPEC: PROGRESS_REPORT_STUCK_REASON_UNCLEAR_SPEC,
                    LEGACY_PROGRESS_REPORT_STUCK_REASON_PERSONAL: PROGRESS_REPORT_STUCK_REASON_PERSONAL,
                    LEGACY_PROGRESS_REPORT_STUCK_REASON_OTHER: PROGRESS_REPORT_STUCK_REASON_OTHER,
                }

                try:
                    v3_progress_report = V3ProgressReport.objects.get(legacy_id=legacy_progress_report.id)
                except ObjectDoesNotExist:
                    v3_progress_report = V3ProgressReport()
                v3_progress_report.legacy_id = legacy_progress_report.id
                v3_progress_report.event = progress_event

                for item in field_map:
                    field_value = getattr(legacy_progress_report, item[1], None)
                    if field_value:
                        setattr(v3_progress_report, item[0], field_value)

                if legacy_progress_report.status:
                    setattr(v3_progress_report, 'status', status_map.get(legacy_progress_report.status, None))

                if legacy_progress_report.stuck_reason:
                    setattr(v3_progress_report, 'stuck_reason', stuck_reason_map.get(legacy_progress_report.stuck_reason, None))

                if not v3_progress_report.migrated_at:
                    v3_progress_report.migrated_at = datetime.datetime.utcnow()

                print('v3_progress_report: ', SimpleProgressReportSerializer(instance=v3_progress_report).data)
                v3_progress_report.save()

                v3_progress_report.created_at = legacy_progress_report.created_at
                v3_progress_report.save()
            else:
                print('progress event not migrated', legacy_progress_report.event.id)

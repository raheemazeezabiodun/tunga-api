from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from tunga_projects.models import Project, Participation, Document, ProgressEvent, ProjectMeta, ProgressReport
from tunga_utils.constants import PROGRESS_REPORT_STATUS_CHOICES, PROGRESS_REPORT_STATUS_STUCK, \
    PROGRESS_REPORT_STUCK_REASON_CHOICES, PROGRESS_REPORT_STATUS_BEHIND_AND_STUCK
from tunga_utils.mixins import GetCurrentUserAnnotatedSerializerMixin
from tunga_utils.serializers import ContentTypeAnnotatedModelSerializer, CreateOnlyCurrentUserDefault, \
    NestedModelSerializer, SimplestUserSerializer, SimpleModelSerializer, \
    SimpleSkillSerializer
from tunga_utils.validators import validate_field_schema


class SimpleProjectSerializer(SimpleModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'title', 'description', 'type', 'budget', 'currency', 'closed', 'start_date', 'deadline')


class SimpleParticipationSerializer(SimpleModelSerializer):
    created_by = SimplestUserSerializer(required=False, read_only=True, default=CreateOnlyCurrentUserDefault())
    user = SimplestUserSerializer()

    class Meta:
        model = Participation
        exclude = ('project',)


class SimpleDocumentSerializer(SimpleModelSerializer):
    created_by = SimplestUserSerializer(required=False, read_only=True, default=CreateOnlyCurrentUserDefault())
    download_url = serializers.CharField(read_only=True)

    class Meta:
        model = Document
        exclude = ('project',)


class SimpleProgressEventSerializer(SimpleModelSerializer):
    created_by = SimplestUserSerializer(required=False, read_only=True, default=CreateOnlyCurrentUserDefault())

    class Meta:
        model = ProgressEvent
        exclude = ('project',)


class SimpleProgressReportSerializer(SimpleModelSerializer):
    user = SimplestUserSerializer(required=False, read_only=True, default=CreateOnlyCurrentUserDefault())
    status_display = serializers.CharField(required=False, read_only=True, source='get_status_display')
    stuck_reason_display = serializers.CharField(required=False, read_only=True, source='get_stuck_reason_display')

    class Meta:
        model = ProgressReport
        exclude = ('event',)


class SimpleProjectMetaSerializer(SimpleModelSerializer):
    created_by = SimplestUserSerializer(required=False, read_only=True, default=CreateOnlyCurrentUserDefault())

    class Meta:
        model = ProjectMeta
        exclude = ('project',)


class ProjectSerializer(
    NestedModelSerializer, GetCurrentUserAnnotatedSerializerMixin, ContentTypeAnnotatedModelSerializer
):
    user = SimplestUserSerializer(required=False, read_only=True, default=CreateOnlyCurrentUserDefault())
    owner = SimplestUserSerializer(required=False, allow_null=True)
    pm = SimplestUserSerializer(required=False, allow_null=True)
    skills = SimpleSkillSerializer(required=False, many=True)
    participation = SimpleParticipationSerializer(required=False, many=True, source='participation_set')
    documents = SimpleDocumentSerializer(required=False, many=True, source='document_set')
    progress_events = SimpleProgressEventSerializer(required=False, many=True, source='progressevent_set')
    meta = SimpleProjectMetaSerializer(required=False, many=True, source='projectmeta_set')

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def save_nested_skills(self, data, instance):
        if data is not None:
            instance.skills = ', '.join([skill.get('name', '') for skill in data])
            instance.save()


class ParticipationSerializer(NestedModelSerializer, ContentTypeAnnotatedModelSerializer):
    created_by = SimplestUserSerializer(required=False, read_only=True, default=CreateOnlyCurrentUserDefault())
    project = SimpleProjectSerializer()
    user = SimplestUserSerializer()

    class Meta:
        model = Participation
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class DocumentSerializer(NestedModelSerializer, ContentTypeAnnotatedModelSerializer):
    created_by = SimplestUserSerializer(required=False, read_only=True, default=CreateOnlyCurrentUserDefault())
    project = SimpleProjectSerializer()
    download_url = serializers.CharField(required=False, read_only=True)

    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ProgressEventSerializer(NestedModelSerializer, ContentTypeAnnotatedModelSerializer):
    created_by = SimplestUserSerializer(required=False, read_only=True, default=CreateOnlyCurrentUserDefault())
    project = SimpleProjectSerializer()
    progress_reports = SimpleProgressReportSerializer(
        required=False, read_only=True, many=True, source='progressreport_set'
    )

    class Meta:
        model = ProgressEvent
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class ProgressReportSerializer(NestedModelSerializer, ContentTypeAnnotatedModelSerializer, GetCurrentUserAnnotatedSerializerMixin):
    user = SimplestUserSerializer(required=False, read_only=True, default=CreateOnlyCurrentUserDefault())
    event = SimpleProgressEventSerializer()
    status_display = serializers.CharField(required=False, read_only=True, source='get_status_display')
    stuck_reason_display = serializers.CharField(required=False, read_only=True, source='get_stuck_reason_display')

    class Meta:
        model = ProgressReport
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def validate(self, attrs):
        errors = dict()

        current_user = self.get_current_user()
        if current_user.is_authenticated():
            BOOLEANS = (True, False)
            required_fields = []

            status_schema = (
                'status', [status_item[0] for status_item in PROGRESS_REPORT_STATUS_CHOICES],
                [
                    (
                        [PROGRESS_REPORT_STATUS_BEHIND_AND_STUCK, PROGRESS_REPORT_STATUS_STUCK],
                        'stuck_reason',
                        [stuck_reason_item[0] for stuck_reason_item in PROGRESS_REPORT_STUCK_REASON_CHOICES]
                    )
                ]
            )
            rate_deliverables_schema = ('rate_deliverables', list(range(1, 6)))  # 1...5

            if current_user.is_developer:
                required_fields = [
                    status_schema,
                    'started_at',
                    ('percentage', list(range(0, 101))),  # 0...100
                    'accomplished',
                    rate_deliverables_schema,
                    'todo',
                    'next_deadline',
                    (
                        'next_deadline_meet', BOOLEANS,
                        [
                            (False, 'next_deadline_fail_reason')
                        ]
                    )
                ]
            elif current_user.is_project_manager:
                required_fields = [
                    status_schema,
                    (
                        'last_deadline_met', BOOLEANS,
                        [
                            (False, 'deadline_miss_communicated', BOOLEANS),
                            (False, 'deadline_report')
                        ]
                    ),
                    'percentage', 'accomplished', 'todo',
                    'next_deadline',
                    (
                        'next_deadline_meet', BOOLEANS,
                        [
                            (False, 'next_deadline_fail_reason')
                        ]
                    ),
                    'team_appraisal'
                ]
            elif current_user.is_project_owner:
                required_fields = [
                    (
                        'last_deadline_met', BOOLEANS,
                        [
                            (False, 'deadline_miss_communicated', BOOLEANS)
                        ]
                    ),
                    ('deliverable_satisfaction', BOOLEANS),
                    rate_deliverables_schema
                ]

            errors.update(validate_field_schema(required_fields, attrs, raise_exception=False))

        if errors:
            raise ValidationError(errors)
        return attrs

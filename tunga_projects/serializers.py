from rest_framework import serializers

from tunga_projects.models import Project, Participation, Document, ProgressEvent
from tunga_utils.mixins import GetCurrentUserAnnotatedSerializerMixin
from tunga_utils.serializers import ContentTypeAnnotatedModelSerializer, CreateOnlyCurrentUserDefault, \
    NestedModelSerializer, SimplestUserSerializer, SimpleModelSerializer, \
    SimpleSkillSerializer


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

    class Meta:
        model = ProgressEvent
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

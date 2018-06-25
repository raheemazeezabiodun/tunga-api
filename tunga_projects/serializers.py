import datetime
from copy import copy

from django.contrib.auth import get_user_model
from rest_framework import serializers

from tunga_projects.models import Project, Participation, Document
from tunga_utils.constants import STATUS_INITIAL
from tunga_utils.mixins import GetCurrentUserAnnotatedSerializerMixin
from tunga_utils.serializers import ContentTypeAnnotatedModelSerializer, CreateOnlyCurrentUserDefault, \
    NestedModelSerializer, SimplestUserSerializer, SimpleModelSerializer, \
    SimpleSkillSerializer


class SimpleProjectSerializer(SimpleModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'title', 'description')


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


class ProjectSerializer(
    NestedModelSerializer, GetCurrentUserAnnotatedSerializerMixin, ContentTypeAnnotatedModelSerializer
):
    user = SimplestUserSerializer(required=False, read_only=True, default=CreateOnlyCurrentUserDefault())
    skills = SimpleSkillSerializer(required=False, read_only=True, many=True)
    participation = SimpleParticipationSerializer(required=False, many=True, source='participation_set')
    documents = SimpleDocumentSerializer(required=False, many=True, source='document_set')

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def save_nested_skills(self, data, instance):
        if data is not None:
            instance.skills = ', '.join([skill.get('name', '') for skill in data])
            instance.save()

    def save_nested_participation(self, data, instance):
        if data:
            for item in data:
                if 'status' in item and item.get('status', None) != STATUS_INITIAL:
                    item['responded_at'] = datetime.datetime.utcnow()
                if type(item['user']) is int:
                    item['user'] = get_user_model().objects.get(pk=item['user'])
                defaults = copy(item)

                current_user = self.get_current_user()
                if current_user and current_user.is_authenticated() and current_user != item.get('user', None):
                    defaults['created_by'] = current_user

                Participation.objects.update_or_create(
                    project=instance, user=item['user'], defaults=defaults)


class ParticipationSerializer(ContentTypeAnnotatedModelSerializer):
    created_by = SimplestUserSerializer(required=False, read_only=True, default=CreateOnlyCurrentUserDefault())
    project = SimpleProjectSerializer()
    user = SimplestUserSerializer()

    class Meta:
        model = Participation
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class DocumentSerializer(ContentTypeAnnotatedModelSerializer):
    created_by = SimplestUserSerializer(required=False, read_only=True, default=CreateOnlyCurrentUserDefault())
    project = SimpleProjectSerializer()

    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

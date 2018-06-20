from tunga_projects.models import Project, Participation
from tunga_utils.mixins import GetCurrentUserAnnotatedSerializerMixin
from tunga_utils.serializers import ContentTypeAnnotatedModelSerializer, SimpleUserSerializer, \
    CreateOnlyCurrentUserDefault, SkillSerializer, NestedModelSerializer


class SimpleParticipationSerializer(ContentTypeAnnotatedModelSerializer):
    user = SimpleUserSerializer()

    class Meta:
        model = Participation
        exclude = ('created_at', 'project')


class ProjectSerializer(NestedModelSerializer, GetCurrentUserAnnotatedSerializerMixin):
    user = SimpleUserSerializer(required=False, read_only=True, default=CreateOnlyCurrentUserDefault())
    participation = SimpleParticipationSerializer(required=False, read_only=True, many=True)
    skills = SkillSerializer(required=False, read_only=True, many=True)

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('created_at',)

    def save_nested_skills(self, data, instance):
        if data is not None:
            instance.skills = ', '.join([skill.get('name', '') for skill in data])
            instance.save()

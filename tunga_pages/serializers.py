from rest_framework import serializers

from tunga_pages.models import SkillPage, SkillPageProfile, BlogPost
from tunga_utils.serializers import SimpleUserSkillsProfileSerializer, SkillSerializer, SimpleUserSerializer, \
    CreateOnlyCurrentUserDefault


class SkillPageProfileSerializer(serializers.ModelSerializer):
    profiles = serializers.JSONField(read_only=True, required=False, source='skillpageprofile_set')
    user = SimpleUserSkillsProfileSerializer(read_only=True, required=False)

    class Meta:
        model = SkillPageProfile
        exclude = ('created_by',)


class SkillPageSerializer(serializers.ModelSerializer):
    profiles = SkillPageProfileSerializer(read_only=True, required=False, source='skillpageprofile_set', many=True)
    skill = SkillSerializer(read_only=True, required=False)

    class Meta:
        model = SkillPage
        exclude = ('created_by',)


class BlogPostSerializer(serializers.ModelSerializer):
    created_by = SimpleUserSerializer(required=False, read_only=True, default=CreateOnlyCurrentUserDefault())

    class Meta:
        model = BlogPost
        fields = '__all__'
        extra_kwargs = {
            'slug': {'required': False, 'allow_blank': True, 'allow_null': True},
        }

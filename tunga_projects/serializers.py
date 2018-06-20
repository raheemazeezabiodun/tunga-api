from rest_framework.serializers import ModelSerializer

from tunga_projects.models import Project


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from dry_rest_permissions.generics import DRYObjectPermissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from tunga_projects.filters import ProjectFilter, DocumentFilter
from tunga_projects.models import Project, Document
from tunga_projects.serializers import ProjectSerializer, DocumentSerializer
from tunga_utils.filterbackends import DEFAULT_FILTER_BACKENDS


class ProjectViewSet(ModelViewSet):
    """
    Project Resource
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, DRYObjectPermissions]
    filter_class = ProjectFilter
    filter_backends = DEFAULT_FILTER_BACKENDS


class DocumentViewSet(ModelViewSet):
    """
    Document Resource
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated, DRYObjectPermissions]
    filter_class = DocumentFilter
    filter_backends = DEFAULT_FILTER_BACKENDS

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from dry_rest_permissions.generics import DRYObjectPermissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from tunga_projects.filterbackends import ProjectFilterBackend
from tunga_projects.filters import ProjectFilter, DocumentFilter, ParticipationFilter, ProgressEventFilter, \
    ProgressReportFilter
from tunga_projects.models import Project, Document, Participation, ProgressEvent, ProgressReport
from tunga_projects.serializers import ProjectSerializer, DocumentSerializer, ParticipationSerializer, \
    ProgressEventSerializer, ProgressReportSerializer
from tunga_utils.filterbackends import DEFAULT_FILTER_BACKENDS


class ProjectViewSet(ModelViewSet):
    """
    Project Resource
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, DRYObjectPermissions]
    filter_class = ProjectFilter
    filter_backends = DEFAULT_FILTER_BACKENDS + (ProjectFilterBackend,)
    search_fields = ('title', 'description')


class ParticipationViewSet(ModelViewSet):
    """
    Participation Resource
    """
    queryset = Participation.objects.all()
    serializer_class = ParticipationSerializer
    permission_classes = [IsAuthenticated, DRYObjectPermissions]
    filter_class = ParticipationFilter
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


class ProgressEventViewSet(ModelViewSet):
    """
    Progress Event Resource
    """
    queryset = ProgressEvent.objects.all()
    serializer_class = ProgressEventSerializer
    permission_classes = [IsAuthenticated, DRYObjectPermissions]
    filter_class = ProgressEventFilter
    filter_backends = DEFAULT_FILTER_BACKENDS


class ProgressReportViewSet(ModelViewSet):
    """
    Progress Report Resource
    """
    queryset = ProgressReport.objects.all()
    serializer_class = ProgressReportSerializer
    permission_classes = [IsAuthenticated, DRYObjectPermissions]
    filter_class = ProgressReportFilter
    filter_backends = DEFAULT_FILTER_BACKENDS

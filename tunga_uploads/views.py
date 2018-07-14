# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from dry_rest_permissions.generics import DRYObjectPermissions
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from tunga_uploads.filters import UploadFilter
from tunga_uploads.models import Upload
from tunga_uploads.serializers import UploadSerializer


class UploadViewSet(viewsets.ModelViewSet):
    """
    Upload Resource
    """
    queryset = Upload.objects.all()
    serializer_class = UploadSerializer
    permission_classes = [IsAuthenticated, DRYObjectPermissions]
    filter_class = UploadFilter

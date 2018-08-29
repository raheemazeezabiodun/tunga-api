import datetime
import json
import os
import re
from operator import itemgetter

import requests
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.utils import six
from rest_framework import viewsets, generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from tunga.settings import MEDIA_ROOT, MEDIA_URL
from tunga_profiles.models import Skill
from tunga_projects.models import Project, ProgressEvent
from tunga_projects.serializers import SimpleProjectSerializer, SimpleProgressEventSerializer
from tunga_utils.models import ContactRequest, InviteRequest, DeveloperRequest
from tunga_utils.serializers import SkillSerializer, ContactRequestSerializer, InviteRequestSerializer, \
    DeveloperRequestSerializer


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Skills Resource
    """
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [AllowAny]
    search_fields = ('name',)


class ContactRequestView(generics.CreateAPIView):
    """
    Contact Request Resource
    """
    queryset = ContactRequest.objects.all()
    serializer_class = ContactRequestSerializer
    permission_classes = [AllowAny]


class InviteRequestView(generics.CreateAPIView):
    """
    Invite Request Resource
    """
    queryset = InviteRequest.objects.all()
    serializer_class = InviteRequestSerializer
    permission_classes = [AllowAny]


class DeveloperRequestView(generics.CreateAPIView):
    """
    Invite Request Resource
    """
    queryset = DeveloperRequest.objects.all()
    serializer_class = DeveloperRequestSerializer
    permission_classes = [AllowAny]


@api_view(http_method_names=['GET'])
@permission_classes([AllowAny])
def get_medium_posts(request):
    r = requests.get('https://medium.com/@tunga_io/latest?format=json')
    posts = []
    if r.status_code == 200:
        try:
            response = json.loads(re.sub(r'^[^{]*\{', '{', r.text))
            posts = [
                dict(
                    title=post['title'],
                    url='https://blog.tunga.io/{}-{}'.format(post['slug'], post['id']),
                    slug=post['slug'], created_at=post['createdAt'],
                    id=post['id'],
                    latestVersion=post['latestVersion']
                )
                for key, post in six.iteritems(response['payload']['references']['Post'])
            ]
            # Sort latest first
            posts = sorted(posts, key=itemgetter('created_at'), reverse=True)
        except:
            pass
    return Response(posts)


@api_view(http_method_names=['GET'])
@permission_classes([AllowAny])
def get_oembed_details(request):
    r = requests.get('https://noembed.com/embed?url=' + request.GET.get('url', None))
    oembed_response = dict()
    if r.status_code == 200:
        oembed_response = r.json()
    return Response(oembed_response)


@api_view(http_method_names=['POST'])
@permission_classes([IsAuthenticated])
def upload_file(request):
    file_response = dict()
    if request.FILES['file']:
        uploaded_file = request.FILES['file']
        store_path = datetime.datetime.utcnow().strftime('uploads/%Y/%m/%d')
        fs = FileSystemStorage(
            location=os.path.join(MEDIA_ROOT, store_path),
            base_url='{}{}/'.format(MEDIA_URL, store_path)
        )
        filename = fs.save(uploaded_file.name, uploaded_file)
        uploaded_file_url = fs.url(filename)
        file_response = dict(url=uploaded_file_url)
    return Response(file_response)


@api_view(http_method_names=['GET'])
@permission_classes([AllowAny])
def find_by_legacy_id(request, model, pk):
    response = None
    try:
        if model == 'task':
            project = Project.objects.get(legacy_id=pk)
            response = SimpleProjectSerializer(instance=project).data
        elif model == 'event':
            progress_event = ProgressEvent.objects.get(legacy_id=pk)
            response = SimpleProgressEventSerializer(instance=progress_event).data
    except ObjectDoesNotExist:
        pass
    if response:
        return Response(response)
    return Response(dict(message='{} #{} replacement found'.format(model, pk)), status=status.HTTP_404_NOT_FOUND)

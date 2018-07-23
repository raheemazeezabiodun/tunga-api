import json

import datetime
from allauth.socialaccount.providers.github.provider import GitHubProvider
from dateutil.relativedelta import relativedelta
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404
from django_countries.fields import CountryField
from dry_rest_permissions.generics import DRYObjectPermissions, DRYPermissions
from rest_framework import viewsets, generics, views, status
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from slacker import Slacker

from tunga_auth.permissions import IsAdminOrCreateOnly
from tunga_payments.models import Invoice
from tunga_profiles.filterbackends import ConnectionFilterBackend
from tunga_profiles.filters import EducationFilter, WorkFilter, ConnectionFilter, DeveloperApplicationFilter, \
    DeveloperInvitationFilter
from tunga_profiles.models import UserProfile, Education, Work, Connection, DeveloperApplication, DeveloperInvitation, \
    Company
from tunga_profiles.serializers import ProfileSerializer, EducationSerializer, WorkSerializer, ConnectionSerializer, \
    DeveloperApplicationSerializer, DeveloperInvitationSerializer, CompanySerializer
from tunga_projects.models import Project, ProgressReport, ProgressEvent
from tunga_tasks.utils import get_integration_token
from tunga_utils import github, slack_utils
from tunga_utils.constants import USER_TYPE_PROJECT_OWNER, APP_INTEGRATION_PROVIDER_SLACK, STATUS_ACCEPTED, \
    STATUS_INITIAL, USER_TYPE_DEVELOPER, \
    PROGRESS_EVENT_DEVELOPER, PROGRESS_EVENT_MILESTONE
from tunga_utils.filterbackends import DEFAULT_FILTER_BACKENDS


class ProfileView(generics.CreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    """
    User Profile Info Resource
    """
    queryset = UserProfile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, DRYObjectPermissions]

    def get_object(self):
        user = self.request.user
        if user is not None and user.is_authenticated():
            try:
                return user.userprofile
            except:
                pass
        return None


class CompanyView(generics.CreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    """
    User Company Info Resource
    """
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, DRYObjectPermissions]

    def get_object(self):
        user = self.request.user
        if user is not None and user.is_authenticated():
            try:
                return user.company
            except:
                pass
        return None


class EducationViewSet(viewsets.ModelViewSet):
    """
    Education Info Resource
    """
    queryset = Education.objects.all()
    serializer_class = EducationSerializer
    permission_classes = [IsAuthenticated, DRYPermissions]
    filter_class = EducationFilter
    search_fields = ('institution__name', 'award')


class WorkViewSet(viewsets.ModelViewSet):
    """
    Work Info Resource
    """
    queryset = Work.objects.all()
    serializer_class = WorkSerializer
    permission_classes = [IsAuthenticated, DRYPermissions]
    filter_class = WorkFilter
    search_fields = ('company', 'position')


class ConnectionViewSet(viewsets.ModelViewSet):
    """
    Connection Resource
    """
    queryset = Connection.objects.all()
    serializer_class = ConnectionSerializer
    permission_classes = [IsAuthenticated, DRYObjectPermissions]
    filter_class = ConnectionFilter
    filter_backends = DEFAULT_FILTER_BACKENDS + (ConnectionFilterBackend,)
    search_fields = ('from_user__username', 'to_user__username')


class DeveloperApplicationViewSet(viewsets.ModelViewSet):
    """
    Developer Application Resource
    """
    queryset = DeveloperApplication.objects.all()
    serializer_class = DeveloperApplicationSerializer
    permission_classes = [IsAdminOrCreateOnly]
    filter_class = DeveloperApplicationFilter
    filter_backends = DEFAULT_FILTER_BACKENDS
    search_fields = ('first_name', 'last_name')

    @list_route(
        methods=['get'], url_path='key/(?P<key>[^/]+)',
        permission_classes=[AllowAny]
    )
    def get_by_key(self, request, key=None):
        """
        Get application by confirmation key
        """
        try:
            application = get_object_or_404(self.get_queryset(), confirmation_key=key, used=False)
        except ValueError:
            return Response(
                {'status': 'Bad request', 'message': 'Invalid key'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = DeveloperApplicationSerializer(application)
        return Response(serializer.data)


class DeveloperInvitationViewSet(viewsets.ModelViewSet):
    """
    Developer Application Resource
    """
    queryset = DeveloperInvitation.objects.all()
    serializer_class = DeveloperInvitationSerializer
    permission_classes = [IsAdminUser]
    filter_class = DeveloperInvitationFilter
    filter_backends = DEFAULT_FILTER_BACKENDS
    search_fields = ('first_name', 'last_name')

    @list_route(
        methods=['get'], url_path='key/(?P<key>[^/]+)',
        permission_classes=[AllowAny]
    )
    def get_by_key(self, request, key=None):
        """
        Get application by invitation key
        """
        try:
            application = get_object_or_404(self.get_queryset(), invitation_key=key, used=False)
        except ValueError:
            return Response(
                {'status': 'Bad request', 'message': 'Invalid key'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = DeveloperInvitationSerializer(application)
        return Response(serializer.data)


class CountryListView(views.APIView):
    """
    Country Resource
    """
    permission_classes = [AllowAny]

    def get(self, request):
        countries = []
        for country in CountryField().get_choices():
            countries.append({'code': country[0], 'name': country[1]})
        return Response(
            countries,
            status=status.HTTP_200_OK
        )


class NotificationView(views.APIView):
    """
    Notification Resource
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, request):
        user = request.user
        if user is not None and user.is_authenticated():
            return user
        else:
            return None

    def get(self, request):
        user = self.get_object(request)
        if user is None:
            return Response(
                {'status': 'Unauthorized', 'message': 'You are not logged in'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user_fields = ['first_name', 'last_name', 'avatar_url']
        profile_fields = ['skills', 'bio', 'country', 'city', 'street', 'plot_number', 'postal_code']
        optional_fields = ['skills', 'bio', 'avatar_url', 'phone_number', 'tel_number']

        if request.user.is_developer or request.user.is_project_manager:
            profile_fields.extend(['id_document', 'phone_number'])
        elif user.is_project_owner and user.tax_location == 'europe':
            profile_fields.extend(['vat_number', 'tel_number'])

        missing_required = []
        missing_optional = []

        for group in [
            [request.user, user_fields],
            [request.user.is_project_owner and request.user.company or request.user.profile, profile_fields]
        ]:
            for field in group[1]:
                if not getattr(group[0], field, None):
                    if field in optional_fields:
                        missing_optional.append(field)
                    else:
                        missing_required.append(field)

        running_projects = Project.objects.filter(
            Q(user=request.user) |
            Q(pm=request.user) |
            Q(owner=request.user) |
            (
                Q(participation__user=request.user) &
                Q(participation__status__in=[STATUS_INITIAL, STATUS_ACCEPTED])
            ), archived=False
        ).distinct()

        unpaid_invoices = Invoice.objects.filter(user=request.user, paid=False, ).order_by('due_at')

        upcoming_progress_events = ProgressEvent.objects.filter(
            ~Q(progressreport__user=request.user),
            project__participation__user=request.user,
            project__participation__status=STATUS_ACCEPTED,
            type__in=[PROGRESS_EVENT_DEVELOPER, PROGRESS_EVENT_MILESTONE],
            due_at__gt=datetime.datetime.utcnow() - relativedelta(hours=24)
        ).order_by('due_at').distinct()

        progress_reports = ProgressReport.objects.filter(
            Q(event__project__user=request.user) |
            Q(event__project__pm=request.user) |
            Q(event__project__owner=request.user),
            user__type=USER_TYPE_DEVELOPER,
            event__type__in=[PROGRESS_EVENT_DEVELOPER, PROGRESS_EVENT_MILESTONE]
        ).distinct()

        return Response(
            {
                'profile': dict(
                    required=missing_required,
                    optional=missing_optional
                ),
                'projects': [dict(
                    id=project.id,
                    title=project.title
                ) for project in running_projects],
                'invoices': [dict(
                    id=invoice.id,
                    title=invoice.title,
                    due_at=invoice.due_at,
                    project=dict(
                        id=invoice.project.id,
                        title=invoice.project.title
                    )
                ) for invoice in unpaid_invoices],
                'events': [dict(
                    id=event.id,
                    title=event.title,
                    type=event.type,
                    due_at=event.due_at,
                    project=dict(
                        id=event.project.id,
                        title=event.project.title
                    )
                ) for event in upcoming_progress_events],
                'reports': [dict(
                    id=report.id,
                    created_at=report.created_at,
                    status=report.status,
                    percentage=report.percentage,
                    user=dict(
                        id=report.user.id,
                        username=report.user.username,
                        display_name=report.user.display_name
                    ),
                    event=dict(
                        id=report.event.id,
                        title=report.event.title,
                        type=report.event.type,
                        due_at=report.event.due_at,
                    ),
                    project=dict(
                        id=report.event.project.id,
                        title=report.event.project.title
                    )
                ) for report in progress_reports],
            },
            status=status.HTTP_200_OK
        )


class RepoListView(views.APIView):
    """
    Repository List Resource
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, provider=None):
        social_token = get_integration_token(request.user, provider, task=request.GET.get('task'))
        if not social_token:
            return Response({'status': 'Unauthorized'}, status.HTTP_401_UNAUTHORIZED)

        if provider == GitHubProvider.id:
            r = github.api(endpoint='/user/repos', method='get', access_token=social_token.token)
            if r.status_code == 200:
                repos = [github.extract_repo_info(repo) for repo in r.json()]
                return Response(repos)
            return Response(r.json(), r.status_code)
        return Response({'status': 'Not implemented'}, status.HTTP_501_NOT_IMPLEMENTED)


class IssueListView(views.APIView):
    """
    Issue List Resource
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, provider=None):
        social_token = get_integration_token(request.user, provider, task=request.GET.get('task'))
        if not social_token:
            return Response({'status': 'Unauthorized'}, status.HTTP_401_UNAUTHORIZED)

        if provider == GitHubProvider.id:
            r = github.api(endpoint='/user/issues', method='get', params={'filter': 'all'},
                           access_token=social_token.token)
            if r.status_code == 200:
                issues = []
                for issue in r.json():
                    if 'pull_request' in issue:
                        continue  # Github returns both issues and pull requests from this endpoint
                    issue_info = {}
                    for key in github.ISSUE_FIELDS:
                        if key == 'repository':
                            issue_info[key] = github.extract_repo_info(issue[key])
                        else:
                            issue_info[key] = issue[key]
                    issues.append(issue_info)
                return Response(issues)
            return Response(r.json(), r.status_code)
        return Response({'status': 'Not implemented'}, status.HTTP_501_NOT_IMPLEMENTED)


class SlackIntegrationView(views.APIView):
    """
    Slack App Integration Info Resource
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, resource=None):
        app_integration = get_integration_token(
            request.user, APP_INTEGRATION_PROVIDER_SLACK, task=request.GET.get('task')
        )
        if app_integration and app_integration.extra:
            extra = json.loads(app_integration.extra)
            slack_client = Slacker(app_integration.token)
            response = None
            if resource == 'channels':
                channel_response = slack_client.channels.list(exclude_archived=True)
                if channel_response.successful:
                    response = channel_response.body.get(slack_utils.KEY_CHANNELS, None)
            else:
                response = {
                    'team': {'name': extra.get('team_name'), 'id': extra.get('team_id', None)},
                    # 'incoming_webhook': {'channel': extra.get('incoming_webhook').get('channel')}
                }
            if response:
                return Response(response, status.HTTP_200_OK)
            return Response({'status': 'Failed'}, status.HTTP_400_BAD_REQUEST)

        return Response({'status': 'Not implemented'}, status.HTTP_501_NOT_IMPLEMENTED)

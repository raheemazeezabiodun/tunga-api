from actstream.models import Action
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from tunga_activity.filters import ActionFilter
from tunga_activity.serializers import ActivitySerializer, ActivityReadLogSerializer


class ActionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Activity Resource
    """
    queryset = Action.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [IsAuthenticated]
    filter_class = ActionFilter
    search_fields = (
        'comments__body', 'messages__body', 'uploads__file', 'messages__attachments__file', 'comments__uploads__file'
    )

    @list_route(
        methods=['post'], url_path='read',
        permission_classes=[IsAuthenticated], serializer_class=ActivityReadLogSerializer
    )
    def update_read(self, request):
        """
        Updates user's read_at for channel
        ---
        serializer: ActivityReadLogSerializer
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

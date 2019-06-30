from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.permissions import ( AllowAny, IsAuthenticated )
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from aparnik.contrib.basemodels.api.serializers import ModelDetailsPolymorphicSerializer
from ..models import Notification


class NotificationListAPIView(ListAPIView):
    serializer_class = ModelDetailsPolymorphicSerializer
    permission_classes = [IsAuthenticated]
    # filter_backends = (filters.SearchFilter,)
    search_fields = ('username', 'last_name', 'first_name')

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.get_this_user(user=user)


class NotificationDetailAPIView(RetrieveAPIView):
    serializer_class = ModelDetailsPolymorphicSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'id'
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        return Notification.objects.get_this_user(user=user)


class NotificationReadAPIView(APIView):
    renderer_classes = (JSONRenderer,)
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None, *args, **kwargs):

        status = HTTP_400_BAD_REQUEST
        content = {
            'success': False,
            'data': {},
            'msg': ''
        }

        try:
            if 'id' in kwargs:
                id = kwargs['id']
                notification = Notification.objects.get(id=id)
                content["data"]['count_update'] = notification.read(user=self.request.user)
            else:
                content["data"]['count_update'] = Notification.objects.read(user=self.request.user)
            content["success"] = True
            status = HTTP_200_OK

        except:

            content["success"] = False
            content["data"] = {}

        return Response(content, status=status)

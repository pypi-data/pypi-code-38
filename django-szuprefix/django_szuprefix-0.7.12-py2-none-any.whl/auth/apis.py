# -*- coding:utf-8 -*-

from . import serializers, signals
from rest_framework import viewsets, decorators, response, status, permissions
from django_szuprefix.api.helper import register, register_urlpatterns
from django.contrib.auth import login as auth_login, models
from rest_framework.serializers import Serializer
from django.utils.six import text_type
from .authentications import USING_JWTA


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Group.objects.all()
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.GroupSerializer


register(__package__, 'group', GroupViewSet)


class UserViewSet(viewsets.GenericViewSet):
    serializer_class = serializers.UserSerializer

    def get_object(self):
        return self.request.user

    @decorators.list_route(['post'], authentication_classes=[], permission_classes=[])
    def login(self, request, *args, **kwargs):
        serializer = serializers.LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.user
            auth_login(request, user)
            data = self.get_serializer(serializer.user).data
            if USING_JWTA:
                from rest_framework_simplejwt.tokens import RefreshToken
                refresh = RefreshToken.for_user(user)
                data['token'] = {'refresh': text_type(refresh), 'access': text_type(refresh.access_token)}
            return response.Response(data)
        return response.Response(serializer.errors, status=400)

    @decorators.list_route(['get'], permission_classes=[permissions.IsAuthenticated])
    def current(self, request):
        srs = signals.to_get_user_profile.send(sender=self, user=request.user, request=request)
        srs = [rs[1] for rs in srs if isinstance(rs[1], Serializer)]
        data = self.get_serializer(request.user, context={'request': request}).data
        for rs in srs:
            opt = rs.Meta.model._meta
            n = "as_%s_%s" % (opt.app_label, opt.model_name)
            data[n] = rs.data
        return response.Response(data)

    @decorators.list_route(['post'])
    def change_password(self, request):
        serializer = serializers.PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return response.Response({})
        return response.Response(serializer.errors, status=400)

    @decorators.list_route(['post', 'get'], authentication_classes=[], permission_classes=[])
    def logout(self, request):
        from django.contrib.auth import logout
        logout(request)
        return response.Response(status=status.HTTP_200_OK)


register(__package__, 'user', UserViewSet, base_name='user')

if USING_JWTA:
    from rest_framework_simplejwt.views import token_obtain_pair, token_refresh
    from django.conf.urls import url

    urlpatterns = [
        url(r'^token/$', token_obtain_pair, name='token_obtain_pair'),
        url(r'^token/refresh/$', token_refresh, name='token_refresh')
    ]
    register_urlpatterns(__package__, urlpatterns)

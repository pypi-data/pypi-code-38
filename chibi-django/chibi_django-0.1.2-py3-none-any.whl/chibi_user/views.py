from .models import User as User_model, Token as Token_model
from .serializers import (
    User as User_serializer, Token as Token_serializer,
    User_create as User_create_serializer
)
from .authentication import Token_simple_authentication
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from chibi_django import view_set
from rest_framework import filters
from django.shortcuts import render


from django.contrib.auth.decorators import login_required

import json


def index( request ):
    return render( request, 'index.html' )


@login_required
def dashboard( request ):
    user = request.user
    auth0user = user.social_auth.get( provider="auth0")
    userdata = {
        'user_id': auth0user.uid,
        'name': user.first_name,
        'picture': auth0user.extra_data['picture']
    }

    return render(
        request, 'dashboard.html',
        {
            'auth0User': auth0user,
            'userdata': json.dumps( userdata, indent=4 )
        } )


class User( view_set.Model_viewset ):
    authentication_classes = [ Token_simple_authentication ]
    permission_classes = [ IsAdminUser ]
    queryset = User_model.objects.all()
    filter_backends = ( filters.OrderingFilter, )
    ordering_fields = ( 'username', 'email' )
    ordering = ( 'username', )
    serializer_class = {
        'default': User_serializer,
        'create': User_create_serializer,
    }

    @detail_route( methods=[ 'POST' ] )
    def refresh_token( self, request, pk, format=None ):
        user = User_model.objects.get( pk=pk )
        token = user.refresh_token()
        serializer = Token_serializer( token )
        return Response( serializer.data )


class Token( view_set.Model_viewset ):
    authentication_classes = [ Token_simple_authentication ]
    permission_classes     = [ IsAdminUser ]
    # queryset               = Token_model.objects.all()
    serializer_class       = Token_serializer

    def get_queryset( self, *args, **kw ):
        user_pk = self.kwargs[ 'users_pk' ]
        return Token_model.objects.filter( user__pk=user_pk )

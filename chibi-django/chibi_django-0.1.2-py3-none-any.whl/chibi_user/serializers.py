from rest_framework import serializers
from chibi_user.models import Token as Token_model, User as User_model
from chibi_django.serializers_fields import (
    parametrise_hyperlink_identity_field
)


class Token( serializers.ModelSerializer ):
    class Meta:
        model = Token_model
        fields = [ 'key', 'create_at' ]


class User( serializers.ModelSerializer ):
    token = Token( required=False )

    class Meta:
        model = User_model
        fields = [ 'pk', 'is_active', 'token' ]
        read_only_fields = [ 'pk', 'is_active', 'token' ]


class User_create( serializers.ModelSerializer ):
    url = parametrise_hyperlink_identity_field(
        lookup_obj_fields=( ( 'pk', 'pk', ), ),
        view_name='users:users-detail' )

    class Meta:
        model = User_model
        fields = [
            'pk', 'url', 'first_name', 'last_name', 'username', 'is_staff',
            'is_superuser', 'is_active' ]
        read_only_fields = [ 'pk', 'url' ]

    def create( self, validate_data ):
        user = User_model.objects.create( **validate_data )
        return user

""" Serializers used throughout the Account Request Rest API
"""
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_mongoengine.serializers import DocumentSerializer

import core_website_app.components.account_request.api as account_request_api
from core_website_app.components.account_request.models import AccountRequest


class AccountRequestSerializer(DocumentSerializer):
    """ Represents the account request serializer
    """
    class Meta:
        model = AccountRequest
        fields = ["id",
                  "username",
                  "first_name",
                  "email",
                  "date"]
        read_only_fields = ('id', 'date',)


class UserSerializer(serializers.ModelSerializer):
    """ Represents the user serializer
    """
    class Meta:
        model = User
        fields = ["id",
                  "username",
                  "first_name",
                  "last_name",
                  "email",
                  "password"]
        read_only_fields = ('id',)

    def create(self, validated_data):
        """ Create and return a new `AccountRequest` instance, given the validated data.
        """
        user = User(username=validated_data['username'],
                    first_name=validated_data['first_name'],
                    last_name=validated_data['last_name'],
                    email=validated_data['email'],
                    password=make_password(validated_data['password']),
                    is_active=False)

        return account_request_api.insert(user)

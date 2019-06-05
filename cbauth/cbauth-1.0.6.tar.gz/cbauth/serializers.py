from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers, exceptions

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email',)
        read_only_fields = ('email', )



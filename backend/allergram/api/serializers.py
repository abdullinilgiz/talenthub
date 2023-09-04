from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
# from rest_framework import serializers

User = get_user_model()


class DjoserUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', )

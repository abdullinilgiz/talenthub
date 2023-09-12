import base64

from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers

from ingredients.models import Ingredient, Allergen, PhotoQuery

User = get_user_model()


class DjoserUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', )


class AllergenSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Allergen
        fields = ('id', 'name', 'user', 'allergen_id', )
        read_only_fields = ('id', 'user', 'allergen_id', )


class GetIngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'is_dangerous', )
        read_only_fields = ('id', 'is_dangerous', )


class GetPhotoQuerySerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    ingredients = GetIngredientsSerializer(many=True)
    image = serializers.ReadOnlyField(source='image.url')

    class Meta:
        model = PhotoQuery
        fields = ('id', 'name', 'image', 'user', 'ingredients')
        read_only_fields = ('id', 'user', 'ingredients')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class PostPhotoQuerySerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    image = Base64ImageField(required=True)

    class Meta:
        model = PhotoQuery
        fields = ('name', 'image', 'user', )
        read_only_fields = ('user', )

    def to_representation(self, instance):
        serializer = GetPhotoQuerySerializer(
            instance,
            context={'request': self.context['request']}
        )
        return serializer.data

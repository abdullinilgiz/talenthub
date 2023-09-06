from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly,
                                        SAFE_METHODS, )
from rest_framework import viewsets, mixins

from api.serializers import (DjoserUserSerializer,
                             AllergenSerializer,
                             GetPhotoQuerySerializer,
                             PostPhotoQuerySerializer, )
from ingredients.models import Allergen, PhotoQuery

User = get_user_model()


class DjoserUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = DjoserUserSerializer
    permission_classes = [AllowAny, ]


class AllergensViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for all allergens in database.

    list: List all Allergen instances

    retrieve: Retrieve Allergen by id

    update: Update Allergen by id

    create: Create Allergen

    destroy: Delete Allergen by id
    """
    queryset = Allergen.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = AllergenSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', ]


class MyAllergensViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for allergens of current user.

    list: List all Allergen inctances of current user

    retrieve: Retrieve Allergen of current user by id 

    update: Update Allergen of current user by id

    create: Create Allergen

    destroy: Delete Allergen of current user by id
    """
    permission_classes = (IsAuthenticated, )
    serializer_class = AllergenSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', ]

    def get_queryset(self):
        return Allergen.objects.filter(user=self.request.user)


class PhotoQueryViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
    ViewSet for all PhotoQuery of current user.

    We create PhotoQuery when user upload photo.

    list: List all PhotoQuery instances of current user

    retrieve: Retrieve PhotoQuery of current user by id

    create: Create PhotoQuery
    """
    permission_classes = (IsAuthenticated, )
    http_method_names = ['get', 'post', ]

    def get_queryset(self):
        return PhotoQuery.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request in SAFE_METHODS:
            return GetPhotoQuerySerializer
        return PostPhotoQuerySerializer

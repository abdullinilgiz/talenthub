from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework.permissions import AllowAny  # , IsAuthenticated

from api.serializers import DjoserUserSerializer

User = get_user_model()


class DjoserUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = DjoserUserSerializer
    permission_classes = [AllowAny, ]

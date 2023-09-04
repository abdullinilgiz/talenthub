from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import DjoserUserViewSet


router = DefaultRouter()
router.register('users', DjoserUserViewSet, basename='users')


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (DjoserUserViewSet, AllergensViewSet, MyAllergensViewSet,
                       PhotoQueryViewSet, )


router = DefaultRouter()
router.register('users', DjoserUserViewSet, basename='users')
router.register('allergens', AllergensViewSet, basename='allergens')
router.register('myallergens', MyAllergensViewSet, basename='myallergens')
router.register('history', PhotoQueryViewSet, basename='history')


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]

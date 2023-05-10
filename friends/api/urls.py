from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CustomUserViewSet,
    FriendViewSet,
    OutgoingRequestViewSet,
    IncomingRequestViewSet,
    UserFriendDeleteViewSet
    )

router = DefaultRouter()
router.register('users', CustomUserViewSet, basename='users')
router.register('friends', FriendViewSet, basename='friends')
router.register(
    'outgoing_request',
    OutgoingRequestViewSet,
    basename='outgoing_request')
router.register(
    'incoming_request',
    IncomingRequestViewSet,
    basename='incoming_request')
urlpatterns = [
    path('', include(router.urls)),
    path('friends_delete/<str:username>/',
    UserFriendDeleteViewSet.as_view({'delete': 'destroy'}),
    name='friends_delete'),
    path('auth/', include('djoser.urls.authtoken')),
]

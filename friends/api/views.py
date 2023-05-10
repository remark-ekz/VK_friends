from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import User, Friend, FriendRequest, UserFriend
from .permissions import AuthorOrReadOnly
from .serializers import (
    CustomUserSerializer,
    FriendSerializer,
    IncomingRequestSerializer,
    OutgoingRequestSerializer,
    UserFriendSerializer
    )


class RetrieveViewSet(
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    pass


class UpdateListRetrieveDestroyViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    pass


class CreateListRetrieveDestroyViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    pass


class CreateListRetrieveViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    pass


class ListViewSet(
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    pass


class CustomUserViewSet(CreateListRetrieveViewSet):
    """Вьюсет для пользователей"""
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny, ]
    @action(
        methods=['get'],
        detail=False,
        url_path='me',
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        user = get_object_or_404(User, username=self.request.user)
        if request.method == 'GET':
            serializer = CustomUserSerializer(
                user,
                context={'request': request},
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return status.HTTP_401_UNAUTHORIZED


class FriendViewSet(ListViewSet):
    """Вьюсет для списка друзей"""
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return Friend.objects.filter(
            user=self.request.user.id,
            )

    
class UserFriendDeleteViewSet(viewsets.ViewSet):
    """Вьюсет для удаления друга"""
    permission_classes = (IsAuthenticated,)

    def destroy(self, request, username):
        user = self.request.user
        friend_for_delete = User.objects.get(username=username)
        user_friend = Friend.objects.get(user=user)
        friend_friend = Friend.objects.get(user=friend_for_delete)
        queryset_1 = UserFriend.objects.filter(
            user=user_friend,
            friend=friend_for_delete)
        queryset_2 = UserFriend.objects.filter(
            user=friend_friend,
            friend=user)
        if not queryset_1.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not queryset_2.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        queryset_1.delete()
        queryset_2.delete()
        return Response({'message': 'Объекты успешно удалены.'})


class OutgoingRequestViewSet(CreateListRetrieveDestroyViewSet):
    """Вьюсет для исходящей заявки"""
    serializer_class = OutgoingRequestSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return FriendRequest.objects.filter(
            offer=self.request.user.id,
            status='active'
            )

    def perform_create(self, serializer):
        serializer.save(offer=self.request.user)


class IncomingRequestViewSet(UpdateListRetrieveDestroyViewSet):
    """Вьюсет для входящей заявки"""
    serializer_class = IncomingRequestSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return FriendRequest.objects.filter(
            accept=self.request.user.id,
            status='active'
            )

    def perform_update(self, serializer):
        accept = self.request.user
        friend_request = serializer.save(accept=accept, status='accepted')
        print(friend_request)
        offer_name = friend_request.offer
        offer = User.objects.get(username=offer_name)
        offer_friend = Friend.objects.get(user=offer)
        accept_friend = Friend.objects.get(user=accept)
        UserFriend.objects.get_or_create(user=offer_friend, friend=accept)
        UserFriend.objects.get_or_create(user=accept_friend, friend=offer)

from django.contrib.auth.hashers import make_password
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.models import User, Friend, FriendRequest, UserFriend


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователей"""
    password = serializers.CharField(write_only=True)
    is_relationships = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'password',
            'is_relationships'
        )

    def validate(self, data):
        invalid_username = ['me', ]
        if data['username'] in invalid_username:
            raise ValidationError('Недопустимый логин')
        return data
    
    def create(self, validated_data):
        validated_data['password'] = (
            make_password(validated_data.pop('password'))
        )
        return super().create(validated_data)

    def get_is_relationships(self, obj):
        user = self.context['request'].user
        if self.context.get('request').user.is_authenticated:
            if user == obj:
                return 'Это вы'
            user_friend = Friend.objects.get(user=user)
            if UserFriend.objects.filter(
                user=user_friend,
                friend=obj
                ).exists():
                return 'Вы друзья'
            elif (
                FriendRequest.objects.filter(
                offer=user,
                accept=obj,
                status='active'
                ).exists()):
                return 'Вы отправили заявку в друзья'
            elif (
                FriendRequest.objects.filter(
                offer=obj,
                accept=user,
                status='active'
                ).exists()):
                return 'Вам отправили заявку в друзья'
            else:
                return 'Вы не состоите в дружеских отношениях'
        else:
            return 'Вы не аутентифицированны'


class UserFriendSerializer(serializers.ModelSerializer):
    """Сериализатор для удаления друзей"""
    user = serializers.CharField(write_only=True)

    class Meta:
        model = UserFriend
        fields = ('friend',)

    def delete(self, instance):
        user = self.instance.user
        user_friend = Friend.objects.get(user=user)
        delete_friend = UserFriend.objects.filter(
            user=user_friend,
            friend=instance.friend)
        delete_friend.delete()
        instance.delete()


class FriendSerializer(serializers.ModelSerializer):
    """Сериализатор друзей"""
    user = CustomUserSerializer(read_only=True)
    friends = CustomUserSerializer(many=True)

    class Meta:
        model = Friend
        fields = (
            'id',
            'user',
            'friends',
            'created'
        )


class OutgoingRequestSerializer(serializers.ModelSerializer):
    """Сериализатор заявки"""
    offer = CustomUserSerializer(read_only=True)
    accept = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = FriendRequest
        fields = (
            'id',
            'offer',
            'accept',
            'status',
            'created'
        )

    def create(self, validated_data):
        # accept_id = validated_data['accept']
        accept_user = User.objects.get(username=validated_data['accept'])
        offer_user = validated_data['offer']
        offer = Friend.objects.get(user=offer_user)
        accept = Friend.objects.get(user=accept_user)
        friend_request = FriendRequest.objects.get(
            offer=accept_user,
            accept=offer_user
            )
        if friend_request:
            friend_request.status = 'accepted'
            friend_request.save()
            UserFriend.objects.get_or_create(user=accept, friend=offer_user)
            UserFriend.objects.get_or_create(user=offer, friend=accept_user)
            return friend_request
        else:
            return FriendRequest(**validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user_serializer = CustomUserSerializer(instance.accept)
        representation['accept'] = user_serializer.data
        return representation


class IncomingRequestSerializer(serializers.ModelSerializer):
    """Сериализатор заявки"""
    offer = CustomUserSerializer(read_only=True)
    accept = CustomUserSerializer(read_only=True)

    class Meta:
        model = FriendRequest
        fields = (
            'id',
            'offer',
            'accept',
            'status',
            'created'
        )

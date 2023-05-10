from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Friend, FriendRequest, UserFriend


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'pk',
        'username',
        'password'
    )
    list_editable = ('password',)
    search_fields = ('username',)
    list_filter = ('username',)
    empty_value_display = '-пусто-'


class FriendsInline(admin.TabularInline):
    model = Friend.friends.through
    verbose_name = u"Friend"
    verbose_name_plural = u"Frinends"


@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'created')
    exclude = ("friends", )
    inlines = (
        FriendsInline,)
    list_editable = ('user',)
    empty_value_display = '-пусто-'


@admin.register(FriendRequest)
class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('pk', 'offer', 'accept', 'status', 'created')
    list_editable = ('offer', 'accept', 'status')
    empty_value_display = '-пусто-'


@admin.register(UserFriend)
class UserFriendAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'friend')

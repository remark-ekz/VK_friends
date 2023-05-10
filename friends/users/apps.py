from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'


class FriendAppConfig(AppConfig):
    name = 'friends'

    def ready(self):
        import users.signals

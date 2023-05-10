from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Friend


@receiver(post_save, sender=User)
def create_user_friend(sender, instance, created, **kwargs):
    if created:
        Friend.objects.create(user=instance)

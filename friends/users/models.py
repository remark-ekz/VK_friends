from django.contrib.auth.models import AbstractUser
from django.db import models


ACCEPTED = 'accepted'
ACTIVE = 'active'
REJECTED = 'rejected'
STATUS_FRIEND = (
    (ACCEPTED, 'accepted'),
    (ACTIVE, 'active'),
    (REJECTED, 'rejected'),
)


class User(AbstractUser):
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
    )
    password = models.CharField(
        'Пароль',
        max_length=150
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Пользователя',
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return str(self.username)


class Friend(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    friends = models.ManyToManyField(
        User,
        blank=True,
        related_name='friends',
        verbose_name='Друзья',
        through='UserFriend'
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Друга',
        verbose_name_plural = 'Друзья'

    def __str__(self):
        return str(self.user)


class UserFriend(models.Model):
    user = models.ForeignKey(Friend, on_delete=models.CASCADE)
    friend = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} {self.friend}'
    
    class Meta:
        ordering = ['-id']
        verbose_name = 'Друга',
        verbose_name_plural = 'Мой друг'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'friend'],
                name='unique_friendship'
            )
        ]


class FriendRequest(models.Model):
    offer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='offers'
    )
    accept = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='accepts'
    )
    status = models.CharField(
        choices=STATUS_FRIEND,
        max_length=50,
        default=ACTIVE
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.offer} - {self.accept} - {self.status}'

    class Meta:
        ordering = ['-id']
        verbose_name = 'Заявку',
        verbose_name_plural = 'Заявки'
        constraints = [
            models.UniqueConstraint(
                fields=['offer', 'accept'],
                name='unique_request'
            )
        ]

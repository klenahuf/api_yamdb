from django.contrib.auth.models import AbstractUser
from django.db import models


USER_ROLE = ['user', 'moderator', 'admin']


class User(AbstractUser):
    role = models.CharField(
        'роль пользователя',
        choices=USER_ROLE,
        default='user',
    )
    bio = models.TextField(
        'Биография',
        blank=True,
    )

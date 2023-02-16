from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import UnicodeUsernameValidator


class User(AbstractUser):
    USER = 'user'
    MODER = 'moderator'
    ADMIN = 'admin'

    USER_ROLES = (
        (MODER, 'Модератор'),
        (ADMIN, 'Администратор'),
        (USER, 'Пользователь'),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.is_superuser:
            self.role = self.ADMIN

    username = models.CharField(
        'имя пользователя',
        max_length=150,
        validators=UnicodeUsernameValidator,
    )
    role = models.CharField(
        'роль пользователя',
        choices=USER_ROLES,
        default=USER,
        max_length=50,
    )
    bio = models.TextField(
        'Биография',
        blank=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_user'
            )
        ]

    @property
    def is_moderator(self):
        return self.role == self.MODER

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_user(self):
        return self.role == self.USER

from django.contrib.auth.models import AbstractUser
from django.db import models


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

    confirmation_code = models.CharField(
        'Код авторизации',
        max_length=150,
        blank=True,
        null=True
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


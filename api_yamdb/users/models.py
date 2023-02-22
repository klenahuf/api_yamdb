from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from users.validators import meUsername


USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'


class User(AbstractUser):

    roles = (
        (USER, USER),
        (MODERATOR, MODERATOR),
        (ADMIN, ADMIN),
    )

    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        unique=True,
        validators=[UnicodeUsernameValidator(), meUsername],
    )

    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(verbose_name='Email', max_length=254,
                              unique=True, blank=False, null=False)
    role = models.CharField(
        verbose_name='Роль пользователя',
        choices=roles,
        max_length=max(len(role[1]) for role in roles), default=USER
    )
    bio = models.TextField(verbose_name='Биография', blank=True)
    confirmation_code = models.CharField(
        verbose_name='Код подтверждения',
        max_length=100,
        null=True,
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return str(self.username)

    @property
    def is_admin(self):
        """Проверка пользователя на наличие прав администратора."""
        return self.role == "admin" or self.is_superuser

    @property
    def is_moderator(self):
        """Проверка пользователя на наличие прав модератора."""
        return self.role == "moderator"

    @property
    def is_user(self):
        """Проверка пользователя на наличие стандартных прав."""
        return self.role == "user"

    class Meta:
        unique_together = ('email',)
        ordering = ('username',)

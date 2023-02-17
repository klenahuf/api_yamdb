import re
from rest_framework.exceptions import ValidationError
from users.models import User


def validate_username(value):
    regex = re.compile(r'^[\w.@+-]+')
    if value == "me":
        raise ValidationError('Недопустимое имя пользователя')
    elif User.objects.filter(username=value).exists():
        raise ValidationError('Такое имя уже есть в базе')
    elif not regex.match(value):
        raise ValidationError('Имя содержит недопустимые символы')
    elif len(value) > 150:
        raise ValidationError('Имя содержит недопустимые символы')


def validate_email(value):
    if User.objects.filter(email=value).exists():
        raise ValidationError('пользователь с таким email уже зарегистрирован')

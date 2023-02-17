from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible



@deconstructible
class UnicodeUsernameValidator(RegexValidator):
    regex = r'^[\w.@+-]+'
    flags = 0




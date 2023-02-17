from django.core.management import commands
from .commands.load_data import Command

commands = {
    'load_data': Command,
}

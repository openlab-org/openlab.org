

from django.contrib import admin
from django.core.management.base import BaseCommand , CommandError
import sys
import os.path

# All locatables

from project.models import Project
from team.models import Team
#from account.models import Profile

from random import choice

from core import util


def do_all(cities, cls):
    # Randomly assigns everything with City and region
    for obj in cls.objects.all():
        obj.regenerate_markdown()
        obj.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        #  do each
        do_all(c, Project)
        do_all(c, Team)
        #do_all(c, Profile)



from django.contrib import admin
from django.core.management.base import BaseCommand , CommandError
import sys
import os.path
from cities_light.models import Country, Region, City

# All locatables
from openlab.project.models import Project
from openlab.team.models import Team
from openlab.accounts.models import Profile

from random import choice

from openlab.core import util


def do_all(cities, cls):
    last_obj = None
    # Randomly assigns everything with City and region
    for obj in cls.objects.all():
        city = choice(cities)
        obj.set_city(city)
        obj.save()
        last_obj = obj

    if not last_obj:
        util.error("Uh oh you dont have any %s, first run testreset" % str(cls))

    # last obj gets a totally random city, just so we have some outliers
    city = City.objects.all().order_by('?')[0]
    last_obj.set_city(city)
    last_obj.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Select from 10 cities
        try:
            c = City.objects.all().order_by('?')[:10]
        except IndexError:
            c = []

        if not c:
            util.error("Uh oh you dont have any cities, first run cities_light")

        #  do each
        do_all(c, Project)
        do_all(c, Team)
        do_all(c, Profile)


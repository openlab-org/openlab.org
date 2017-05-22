from django.contrib import admin
from django.core.management.base import BaseCommand , CommandError
import sys
import os.path
from openlab.users.models import User
from datetime import datetime
from django.conf import settings
from django.core import serializers

from cities_light.models import Country, Region, City
import random


def random_object(qs, retries=40):
    count = qs.count()
    if count:
        index = random.randint(0, count-1)
        try:
            return qs[index]
        except IndexError:
            if retries > 0:
                return random_object(qs, retries=retries-1)
            else:
                raise Exception("too many retries!")
    else:
        raise Exception("Random on empty queryset!")

extra_city_names = [
    "new york",
    "sao paulo",
    "los angeles",
    "porto alegre, rs",
    "seattle",
    "rio de janeiro",
    "recife, pe",
    "madrid",
    "barcelona",
    "london",
    "tokyo",
    "paris",
    "beijing",
    "milwaukee",
    "san francisco, ca",
]

class Command(BaseCommand):
    def handle(self, *a, **k):
        assert len(a) == 1
        filename = a[0]
        assert filename.endswith(".json")

        # Get all countries
        countries = list(Country.objects.all())

        # Get 100 random cities + regions
        qs = City.objects.all()
        cities = [random_object(qs) for i in xrange(100)]

        # Add a few famous ones for sure
        for name in extra_city_names:
            extra = list(City.objects.filter(search_names__icontains=name))
            cities.extend(extra)

        # Add all relevant regions
        regions = [city.region for city in cities]

        # Now serialize all data
        all_data = countries + regions + cities
        with open(filename, "w") as out:
            serializers.serialize("json", all_data, stream=out)



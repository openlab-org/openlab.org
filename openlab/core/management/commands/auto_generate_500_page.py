from django.contrib import admin
from django.core.management.base import BaseCommand , CommandError
import sys
import os.path
from cities_light.models import Country, Region, City

# All locatables
from random import choice

from django.template.loader import render_to_string

from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        settings.DEBUG = False
        settings.TEMPLATE_DEBUG = False
        string = render_to_string("error/500_base.html", {
                'STATIC_URL': settings.STATIC_URL,
            })
        path = os.path.join(settings.DJANGO_ROOT, 'templates', '500.html')
        if os.path.exists(path) and 'force' not in args:
            print("%s exists. Continue?" % path)
            if not input('Enter "y[es]" to continue '
                    '(pass "force" to skip): ').lower().startswith('y'):
                print('lol okay.')
                sys.exit(1)

        with open(path, 'w+') as f:
            f.write(string)


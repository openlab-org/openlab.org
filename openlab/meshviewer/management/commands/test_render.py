from django.contrib import admin
from django.core.management.base import BaseCommand , CommandError
import sys
import os.path
from openlab.users.models import User
from datetime import datetime
from django.conf import settings

from ... import utils

class Command(BaseCommand):
    def handle(self, *a, **k):
        for p in a:
            abs_path = os.path.abspath(p)
            utils.render_to_png(abs_path, abs_path+".png")


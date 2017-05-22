
from django.core.management.base import BaseCommand , CommandError

from core.util import get_celery_worker_status
import json
import sys

class Command(BaseCommand):
    def handle(self, *args, **options):
        json.dumps(get_celery_worker_status(), indent=4)



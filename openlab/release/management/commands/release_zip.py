from django.contrib import admin
from django.core.management.base import BaseCommand , CommandError
import sys
import os.path
from datetime import datetime
from django.conf import settings
from django.core import serializers

from release.models import Release

# 1st party
from openlab.core.s3utils import S3Connection
from openlab.users.models import User
from openlab.release import util, tasks

actions = {}

def test_zip(release_id):
    release = Release.objects.get(id=release_id)

    #s3conn = S3Connection()

    # This is the huge, blocking step of actually creating the zip
    zip_path = util.make_zip(release)
    size = os.path.getsize(zip_path)

    print "---------------------------------------"
    print "- Results                             -"
    print "---------------------------------------"
    print "PATH: ", zip_path
    print "SIZE: ", size


def test_task(release_id):
    tasks.create_preview(release_id, force=True)

actions['test_zip'] = test_zip
actions['test_task'] = test_task



class Command(BaseCommand):
    def handle(self, *a, **k):
        try:
            action = a[0]
            assert action in actions
        except:
            print("Needs action, one of %s" % actions.keys())
            sys.exit(1)

        try:
            release_id = int(a[1])
        except:
            print("Needs to be something like: test_zip 123 "
                "(where 123 is the ID of the Release object)")
            sys.exit(1)

        actions[action](release_id)


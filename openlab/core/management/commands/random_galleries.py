from glob import glob
import sys
import os.path
from random import randint, choice, choice, choice, choice
from datetime import datetime
from django.conf import settings
from django.contrib import admin
from django.core.management.base import BaseCommand , CommandError

from random_words import RandomWords

from openlab.users.models import User
from openlab.moderation.models import FeaturedProject
from openlab.gallery.upload_utils import save_photo
from openlab.gallery.models import Photo, Gallery
from openlab.project.models import Project
from openlab.project.models import Team
from openlab.core import util

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Make some users
        d = os.path.join('/tmp', 'ol_random_photos')
        ERR = "You need to run './tools/download_random_photos.sh' first."
        if not os.path.exists(d):
            print(ERR)
            sys.exit(1)

        try:
            projs = list(Project.objects.all()[:12])
            teams = list(Team.objects.all()[:5])
        except Exception as e:
            print(repr(e))
            print("Need projects + teamsfirst prolly")
            sys.exit(1)

        images = [(p, os.path.basename(p)) for p in glob(os.path.join(d, "*"))]

        if len(images) < 20:
            print(("Not enough images in " + d + ", looking for at "+
                    "least 20." + ERR))
            sys.exit(1)

        # gets featured projects
        projs = list(FeaturedProject.get_featured_projects())

        #projs.extend()

        # Oh and get 12 last updated projects
        projs.extend(list(Project.objects.all()[:12]))
        for temp_file_name, filename in images:
            obj = choice(projs)

            gallery = obj.create_gallery_if_necessary()
            # Create a new Photo obj
            photo = Photo(gallery=gallery)

            # Actually save the photo
            save_photo(temp_file_name, filename, photo, gallery)
            print("savE_photo", temp_file_name, filename, photo, gallery)

            if not obj.photo:
                obj.photo = photo
                obj.save()


        util.trace("Loaded %i images" % len(images))


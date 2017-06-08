# python
import re
import json
import os
import tempfile
import subprocess
import random
import datetime
from codecs import open
from django.template.loader import render_to_string

# django
from django.forms import model_to_dict

# first party
from openlab.core.util import makedirs_to_path, download_file

r"""
Project_name_v1.3.0.zip
    |- Project_name_v1.3.0/
        |- license.txt       # License content
        |- openlab.txt       # About Open Lab and how to get to the project page 
        |- readme.html       # "Frozen" html file that is the rel description
        |- manifest.html     # Description of all components and files, images
        |- Manual_override/  # individual components
            |- Stuff.pdf
            |- model_thing.stl
        |- Platform/
            |- Stuff.pdf
        |- _images/          # Rendered previews
            |- Stuff.preview.png
            |- Stuff.thumb.png
            |- model_thing.preview.png
            |- model_thing.thumb.png
        
"""


def auto_version(previous=None):
    if not previous or not previous.version:
        return "1.0"
    version = previous.version
    split_version = str(version).split(".")
    if split_version[0].isdigit():
        split_version[0] = str(int(split_version[0]) + 1)
    return ".".join(split_version)

def gallery_to_list(object_list, enabled=False):
    result = []
    for obj in object_list:
        d = {
            'id': obj.id,
            'model': obj.model,
            'enabled': enabled,
            'preview_image_thumb': obj.preview_image_thumb or None,
            'preview_image': obj.preview_image or None,
            'preview_file': obj.preview_file or None,
            #'preview_html': obj.preview_html,
        }
        if hasattr(obj, 'url'):
            # Is a media link URL
            d.update({
                    'url': obj.url or None,
                    'source': obj.source or None,
                    #'preview_html': obj.preview_html,
                })

        d['description'] = getattr(obj, 'description', None) or None
        d['title'] = getattr(obj, 'title', None) or None

        result.append(d)

    return result


def auto_media(project, previous=None):
    if previous:
        # TODO do something else
        pass

    gallery = project.gallery

    project_photos = list(gallery.photos.all())
    project_media = list(gallery.medialinks.all())
    project_files = list(project.tip_revision.files.all())
    simple_list = project_photos + project_media + project_files
    return simple_list

    #  eventually if we make a more complicated interactive one we use the
    #  following and go full JSON / JS
    lst = []

    lst.extend(gallery_to_list(project_photos, True))
    lst.extend(gallery_to_list(project_media, True))
    lst.extend(gallery_to_list(project_files, False))

    return json.dumps(lst)



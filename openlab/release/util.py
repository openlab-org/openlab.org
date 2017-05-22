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


def _urlize(d, field):
    d[field] = d[field].url if d.get(field) else None

def file_model_to_dict(file_model):
    # Serialize file model to a nice dict format to be immortalized in a
    # project release
    d = model_to_dict(file_model)
    _urlize(d, 'preview_file')
    _urlize(d, 'preview_image_thumb')
    _urlize(d, 'preview_image')
    _urlize(d, 'path')
    d['photo'] = d['photo'].preview_image.url if d.get('photo') else None
    d['photo_thumb'] = d['photo'].preview_image_thumb.url if d.get('photo') else None
    d['get_extension'] = str(file_model.get_extension())
    d['preview_ready'] = bool(file_model.preview_ready)
    d['preview_tried_date'] = str(d.get('preview_tried_date'))
    return d

CHARS = re.compile(r'[\W_-]+')
def sanitize_title(s):
    return CHARS.sub('_', s).strip('_')

def beautify(s):
    return CHARS.sub(' ', s).strip().capitalize()

ZIP_BIN_PATH = "/usr/bin/zip"
def zip_folder(folder_path, zip_path):
    """
    Zips given folder into path provided by zip_path
    """
    # Use unix zip file creator (instead of python), since its faster, lower
    # memory, and easier
    args = [ZIP_BIN_PATH, "-9", "-r", zip_path, folder_path]
    return subprocess.check_call(args)


def _get_tmp():
    i = datetime.datetime.now()
    base_path = os.path.join(tempfile.gettempdir(),
            'openlab_release',
            "%s_%s_%s" % (i.year, i.month, i.day))

    if os.path.exists(base_path) and False:
        # to prevent collisions of multiple releases of the same project with
        # the same version number on same day, right now disabled for testing
        base_path = os.path.join(base_path,
                "%05i" % random.randint(0, 99999))

    return base_path

THUMB_PATH = '_images'

def make_zip(release):
    project = release.project

    # Generate path
    title = sanitize_title(project.title)
    folder_name = u"%s_v%s" % (title, release.version)
    filename = "%s.zip" % folder_name
    base_path = _get_tmp()

    # Full path for temp directories
    zip_path = os.path.join(base_path, filename)
    folder_path = os.path.join(base_path, folder_name)

    components = [] # store resulting paths here

    # Loop through every component, doing any dowloads / copies necessary to
    # build the directory structure
    for component in release.components:
        title = component.get(u'title', '')
        c = dict(component)
        component_folder = os.path.join(folder_path, sanitize_title(title))
        c['folder'] = sanitize_title(title)
        components.append(c)

        c['files'] = []

        for f_info in component.get('files', []):
            file_name = f_info[u'filename']

            # 1. Download file from S3 to folder_path
            file_url = f_info[u'path']
            relative_path = os.path.join(c['folder'], file_name)
            dest_path = os.path.join(folder_path, relative_path)
            makedirs_to_path(dest_path)
            download_file(file_url, dest_path)

            # 2. Download thumb from S3 to folder_path (if it exists)
            thumb_filename = sanitize_title(file_name)+ ".thumb.jpg"
            dest_path = os.path.join(folder_path, THUMB_PATH, thumb_filename)
            image_url = f_info.get('preview_image_thumb')
            if image_url:
                makedirs_to_path(dest_path)
                download_file(image_url, dest_path)

            # Assemble dict to be included in context when rendering manifest.html
            c['files'].append({
                    "filename": file_name,
                    "relative_path": relative_path,
                    "ext": f_info.get('get_extension'),
                    "thumb_filename": thumb_filename if image_url else None,
                    "file_name": file_name,
                    "size": f_info.get('size') or 0,
                })

    info_files = [
            "license.txt",
            "readme.html",
            "manifest.html",
            "openlab.txt",
        ]

    template_base_path = "release/zip"

    ctx = {
        "release": release,
        "project": project,
        "components": components,
        "THUMB_PATH": THUMB_PATH,
    }

    # Generate info files
    for info_file_name in info_files:
        dest_path = os.path.join(folder_path, info_file_name)

        # Render & write preview HTML
        template_path = os.path.join(template_base_path, info_file_name)
        html = render_to_string(template_path, ctx)

        with open(dest_path, "w+", encoding="utf-8") as f:
            # Use Windows new-lines for maximum cross-compatibility
            html = html.replace("\r\n", "\n").replace("\n", "\r\n")
            f.write(html)
    
    # Ultimate
    zip_folder(folder_path, zip_path)

    return zip_path


def auto_version(previous=None):
    if not previous or not previous.version:
        return "1.0"
    version = previous.version
    split_version = str(version).split(".")
    if split_version[0].isdigit():
        split_version[0] = str(int(split_version[0]) + 1)
    return ".".join(split_version)


def _get_field_path(obj, field_name):
    f = getattr(obj, field_name, False)
    if not f:
        return False
    return f.url()

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


def auto_componentize(project, previous=None):
    """
    Figure out a reasonable layout for components:
    """

    #components = [
    #    {
    #        "title": "...",
    #        "summary": "",
    #        "files": [
    #            {
    #            }
    #        ]
    #    }
    #]
    components = {}

    if previous:
        # inherit those components
        pass

    files = list(project.files.all())

    def set_folder(folder_name, file_dict):
        # todo: add in folder here
        components.setdefault(folder, {
                "id": folder,
                "title": beautify(folder),
                "summary": "",
                "files": []
            })
        components[folder_name]['files'].append(file_dict)
        return components

    # look for folders
    for file_model in files:
        folder = file_model.folder or "core"
        file_dict = file_model_to_dict(file_model)
        set_folder(folder, file_dict)

    # include sub-projects
    subprojects = list(project.dependencies.all())
    for proj in subprojects:
        subproj_files = list(proj.files.all())
        if not subproj_files:
            continue # empty subproject, skip

        components[proj.hubpath] = {
            "id": proj.hubpath,
            "title": proj.title,
            "summary": proj.summary,
            "files": map(file_model_to_dict, subproj_files),
        }

    # return just the components as a list
    return components.values()



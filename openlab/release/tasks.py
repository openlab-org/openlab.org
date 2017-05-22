import os.path

# 1st party
#from openlab.taskapp import app
from openlab.core.s3utils import S3Connection

# local
from . import util
from .models import Release

# TODO fix
#@app.task(ignore_result=True, name="release_create_release")
def create_preview(release_id, force=False):

    release = Release.objects.get(id=release_id)

    if release.zip_path and not force: # skip, already done!
        return

    s3conn = S3Connection()

    # This is the huge, blocking step of actually creating the zip
    zip_path = util.make_zip(release)

    # now we save the zip info
    release.size = os.path.getsize(zip_path)

    # And we upload it!
    release.zip_path = s3conn.upload_as_filefield(
                zip_path, release, release.zip_path)
    release.save()

    # layout of command:
    # obj.field = s3conn.upload_as_filefield(local_path, obj, obj.field)


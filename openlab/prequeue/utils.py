# python
import sys
import os
import datetime

# django
from django.conf import settings

# 1st party -- pull in S3Connection wrapper
from openlab.core.s3utils import S3Connection

def ensure_directory_exists(path):
    # Make sure the directory exists
    try:
        os.makedirs(os.path.dirname(path))
    except OSError:
        pass


def get_temp_dir(id_):
    """
    Returns a fairly unique temp directory based on the given ID
    """
    i = datetime.datetime.now()
    base_path = os.path.join('/tmp',
                    settings.SITE_NAME,
                    # Put into daily folders so we can easily check
                    "pq_%s_%s_%s" % (i.year, i.month, i.day),
                    "%06i_%06i" % (id_, i.microsecond))
    ensure_directory_exists(os.path.abspath(base_path))
    return base_path


chop_ext = lambda s: os.path.splitext(s)[0]
def path_builder(base, type_, filename):
    """
    Assembles thumb/image/file paths
    """
    new_filename = "%s.%s" % (type_, chop_ext(filename))
    return os.path.join(base, new_filename)



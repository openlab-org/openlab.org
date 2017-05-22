import sys
import os
import stat

# 3rd party
import requests

####################################################################
# Terminal output functions
# A few functions for making output to the terminal neater
####################################################################
class Term:
    bold = "\033[1m"
    reset= "\033[0;0m"
    purple = '\033[95m'
    blue = '\033[94m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    Bold = staticmethod(lambda s: Term.bold + s + Term.reset)
    Blue = staticmethod(lambda s: Term.blue + s + Term.reset)
    Yellow = staticmethod(lambda s: Term.yellow + s + Term.reset)
    Green = staticmethod(lambda s: Term.green + s + Term.reset)
    Red = staticmethod(lambda s: Term.red + s + Term.reset)
    Purple = staticmethod(lambda s: Term.purple + s + Term.reset)

def warning(msg):
    sys.stderr.write(Term.Yellow("Warning: ") + Term.Bold(msg) + "\n")

def trace(msg):
    sys.stdout.write(Term.Blue("---> ") + msg + "\n")


def error(msg):
    sys.stderr.write("\n-----------------------------\n")
    sys.stderr.write(Term.Red("Fatal Error: ") +
            Term.Bold(msg) + "\n")
    sys.exit(1)


# Set files to rw-r--r--
#                 r               w        -   r         --  r--
FILE_PERM =    stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH

# Set directories to rwxr-xr-x
DIR_PERM =    FILE_PERM | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH

def recursive_permissions_on_path(path):

    for root, dirs, files in os.walk(path):
        for d in dirs:
            # Set folders to rwxr-xr-x
            os.chmod(os.path.join(root, d), DIR_PERM)
        for f in files:
            # Set files to rwxr-xr-x
            os.chmod(os.path.join(root, f), FILE_PERM)


def makedirs_to_path(full_new_path):
    # Make sure the directory exists
    try:
        os.makedirs(os.path.dirname(full_new_path))
    except OSError:
        pass



def expire_view_cache(view_name, args=[], namespace=None, key_prefix=None):
    """
    http://stackoverflow.com/questions/2268417/expire-a-view-cache-in-django

    This function allows you to invalidate any view-level cache. 
        view_name: view function you wish to invalidate or it's named url pattern
        args: any arguments passed to the view function
        namepace: optioal, if an application namespace is needed
        key prefix: for the @cache_page decorator for the function (if any)
    """
    from django.core.urlresolvers import reverse
    from django.http import HttpRequest
    from django.utils.cache import get_cache_key
    from django.core.cache import cache
    # create a fake request object
    request = HttpRequest()
    # Loookup the request path:
    if namespace:
        view_name = namespace + ":" + view_name
    request.path = reverse(view_name, args=args)
    # get cache key, expire if the cached item exists:
    key = get_cache_key(request, key_prefix=key_prefix)
    if key:
        if cache.get(key):
            # Delete the cache entry.  
            #
            # Note that there is a possible race condition here, as another 
            # process / thread may have refreshed the cache between
            # the call to cache.get() above, and the cache.set(key, None) 
            # below.  This may lead to unexpected performance problems under 
            # severe load.
            cache.set(key, None, 0)
        return True
    return False


def expire_url_cache(path):
    # create a fake request object
    request = HttpRequest()
    # Loookup the request path:
    request.path = path
    # get cache key, expire if the cached item exists:
    key = get_cache_key(request)
    if key:
        # Delete the cache entry.  
        cache.set(key, None, 0)
        return True
    return False

def get_celery_worker_status():
    ERROR_KEY = "ERROR"
    try:
        from celery.task.control import inspect
        insp = inspect()
        d = insp.stats()
        if not d:
            d = { ERROR_KEY: 'No running Celery workers were found.' }
    except IOError as e:
        from errno import errorcode
        msg = "Error connecting to the backend: " + str(e)
        if len(e.args) > 0 and errorcode.get(e.args[0]) == 'ECONNREFUSED':
            msg += ' Check that the RabbitMQ server is running.'
        d = { ERROR_KEY: msg }
    except ImportError as e:
        d = { ERROR_KEY: str(e)}
    return d


# By default, download in 128 Kb chunks, streaming to disk
def download_file(url, destination=None, chunk_size=128*1024):
    """
    Downloads file from URL to (optional) destination
    """
    if not destination:
        destination = url.split('/')[-1]

    # Use the stream=True parameter to get streaming to disk
    r = requests.get(url, stream=True)
    with open(destination, "wb") as f:
        for chunk in r.iter_content(chunk_size=chunk_size): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
                os.fsync(f.fileno())
    return destination




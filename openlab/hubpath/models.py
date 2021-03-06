from django.db import models
from django.conf import settings
from django.apps import apps
from django.core.cache import cache
from django.utils.translation import ugettext as _
from django.core.exceptions import FieldError, ImproperlyConfigured,\
                    ObjectDoesNotExist, MultipleObjectsReturned, ValidationError

split_model_names = getattr(settings,
        'HUBPATH_MODELS_SPLIT',
        [
            ('project', 'Project'),
        ])

single_model_names = getattr(settings,
        'HUBPATH_MODELS_SINGLE',
        [
            ('team',    'Team'),
            ('accounts', 'Profile'),
        ])



def make_path(instance):
    """
    Computes a path for the given instance.
    """
    name = instance.__class__.__name__
    for app_name, model_name in single_model_names:
        if name == model_name:
            # Found! It's a single one
            return instance.slug

    for app_name, model_name in split_model_names:
        if name == model_name:
            # Found! It's a double one
            if instance.team:
                prefix = instance.team.slug
            else:
                prefix = instance.user.username
            return "%s/%s" % (prefix, instance.slug)

    # Could not find anywhere
    raise HubPathBase.ConfigError("%s uses HubPath but "
                            "was not listed in config." % name)


class AutoProjectPathField(models.CharField):
    """
    Field that allows "namespaced" slugs, GitHub style.

    (Presently not in use, in lieu of just doing in Save constructor.)
    """
    def __init__(self, *a, **k):
        k.setdefault('max_length', 255)
        k.setdefault('editable', False)
        k.setdefault('unique', True)
        k.setdefault('db_index', True)
        models.CharField.__init__(self, *a, **k)

    def pre_save(self, instance, add):
        super(AutoProjectPathField, self).pre_save(instance, add)
        val = make_path(instance)
        setattr(instance, self.attname, val)
        return val


class HubPathObjects(object):
    class ConfigError(ImproperlyConfigured): pass
    class DoesNotExist(ObjectDoesNotExist): pass
    class DuplicateHubPath(ValidationError): pass

    KEY_PREFIX = 'hubpath:path:%s'
    def get_from_model_list(self, hubpath, model_names):
        for app_name, model_name in model_names:
            model = apps.get_model(app_name, model_name)
            if not model:
                # XXX Not found
                print("ERROR NOT FOUND " , app_name, model_name) 
                continue
            try:
                return model.objects.get(hubpath=hubpath)
            except model.DoesNotExist:
                pass

        return False

    @staticmethod
    def cache_key(hubpath):
        return HubPathObjects.KEY_PREFIX % (hubpath)

    @classmethod
    def check_cache(cls, hubpath):
        return cache.get(cls.cache_key(hubpath))

    @classmethod
    def clear_cache(cls, hubpath):
        cache.delete(cls.cache_key(hubpath))

    @classmethod
    def set_cache(cls, result, value=None):
        if value is None:
            value = result

        cache.set(cls.cache_key(result.hubpath), value)

    def get(self, hubpath, path_context=''):

        # idea: implement "path_context", where we in fact cache the entire
        # context for a page in a single memcached query. Each page can have
        # its own cache, ie "hubpath:team/project:overview". If it fails with
        # a call there, it then builds the context & saves it in the view (and
        # just uses "hubpath:team" as a fallback)

        cached = self.check_cache(hubpath)
        if cached is False:
            # "False" means not exists (ie, deleted)
            raise HubPathBase.DoesNotExist()

        if cached:
            # True values means existing
            return cached

        # Not in cache, this should only happen if the cache is full or
        # disabled or something
        if '/' in hubpath:
            # Split hubpath
            result = self.get_from_model_list(hubpath, split_model_names)
        else:
            # Single hubpath
            result = self.get_from_model_list(hubpath, single_model_names)

        if not result:
            raise HubPathBase.DoesNotExist()

        self.set_cache(result)
        return result

    def is_available(self, hubpath, obj_id=False):
        """
        Checks if given HubPath is available. Pass obj_id to exclude current
        object.
        """
        try:
            result = self.get(hubpath)
        except HubPathBase.DoesNotExist:
            # Doesn't exist at all, definitely available
            return True

        if not result:
            # Essentially is failure, should return that its avilable
            return True

        if isinstance(result, str):
            # Weird bug during unittests
            return True

        #except MultipleObjectsReturned:
        #    # Shouldn't ever happen, but definitely in use
        #    return False

        # If we have passed an object_id, then 
        if result.id == obj_id:
            # it's just me, it is available for me to use
            return True
        else:
            # it's not me, return false, not available
            return False
        # (verbose code for clarity of comments)
        #return obj.id != obj_id

    @staticmethod
    def arbitrary_get(**kwds):
        """
        Get the first HubPath based object with the given parameters that it
        finds.

        Note: QUITE DB expensive, should only use in non-time critical
        locations.
        """
        for app_name, model_name in split_model_names + single_model_names:
            model = apps.get_model(app_name, model_name)
            if not model:
                raise HubPathBase.ConfigError("%s.%s was listed in config,"
                                    " but not found." % app_name, model_name)
                continue

            try:
                return model.objects.get(**kwds)
            except model.DoesNotExist:
                # Simply couldn't find
                pass
            except FieldError:
                # Filter not appropriate for this model
                pass

        # not found
        raise HubPathBase.DoesNotExist()


class HubPathBase(models.Model):
    ConfigError = HubPathObjects.ConfigError
    DoesNotExist = HubPathObjects.DoesNotExist
    DuplicateHubPath = HubPathObjects.DuplicateHubPath

    class Meta:
        abstract = True

    slug = models.SlugField(max_length=32, db_index=False, unique=False)

    hubpath = models.CharField(
            #editable=False,
            unique=True,
            db_index=True,
            max_length=96,
            help_text=_("Absolute URL for this, ie "
                "'team-name/project-name' or 'team-name'"))

    hubpath_objects = HubPathObjects()

    # Used by unittests to remove the need to flush the db every time, and
    # specify in every save command it as a default
    _SKIP_HUBPATH_CHECK = False

    def get_url_arg(self):
        """
        Returns value of the main string used in URLs to access this object.
        """
        return self.hubpath

    def save(self, *a, **k):
        """
        Generate hubpath if not already specified
        """
        if not self.hubpath:
            self.hubpath = make_path(self)

        if ((not k.get('skip_hubpath_check') and not self.id)\
                        or k.get('force_hubpath_check'))\
                        and not self._SKIP_HUBPATH_CHECK:

            # Predict what HubPath will be generated
            if not self.hubpath_objects.is_available(self.hubpath, bool(self.id)):
                raise HubPathBase.DuplicateHubPath('HubPath: path already in use. '
                                '(use skip_hubpath_check to skip check)')

        # clear out our keywords
        if k.get('force_hubpath_check'):
            del k['force_hubpath_check']
        if k.get('skip_hubpath_check'):
            del k['skip_hubpath_check']

        super(HubPathBase, self).save(*a, **k)

    def save_cache(self):
        """
        Should call this after every save.
        """
        self.hubpath_objects.set_cache(self)

    def delete_cache(self, permadelete=False):
        """
        Should call this after deleting, to create a 404 that immediately
        resolves as a 404 (and thus is "off limits" until the cache is
        cleared).
        """
        if permadelete:
            # Actual delete
            self.hubpath_objects.clear_cache(self.hubpath)
        else:
            # "False" means that it should be a 404
            self.hubpath_objects.set_cache(self, False)


# Alias
hubpath_objects = HubPathBase.hubpath_objects

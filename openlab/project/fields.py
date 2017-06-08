from django.db import models
from django.core.validators import RegexValidator

from licensefield.fields import LicenseField


version_number_validator = RegexValidator(regex=r'^\d+\.\d+(\.\d+)?(a|b|rc\d+)?$',
                                message='Must be in the form of 1.0 or 1.0.0, '
                                        'optionally followed by "a" (alpha), '
                                        '"b" (beta), or "rc1" (release candidate '
                                        '1)',
                                code='nomatch')


class VersionNumberField(models.CharField):
    """
    Field that allows versioning
    """
    def __init__(*a, **k):
        k['max_length'] = 24
        k['validators'] = [version_number_validator]
        models.CharField.__init__(*a, **k)


class AutoProjectPathField(models.CharField):
    """
    Field that allows "namespaced" slugs, GitHub style
    """
    def __init__(self, *a, **k):
        k.setdefault('max_length', 255)
        k.setdefault('editable', False)
        k.setdefault('unique', True)
        k.setdefault('db_index', True)
        self.make_path = k['make_path']
        del k['make_path']
        models.CharField.__init__(self, *a, **k)

    def pre_save(self, instance, add):
        super(AutoProjectPathField, self).pre_save(instance, add)
        val = self.make_path(instance, add)
        setattr(instance, self.attname, val)
        return val


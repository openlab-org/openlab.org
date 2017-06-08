from django.db import models
from django.utils.translation import ugettext as _
from django.db.models import Max

class ScopeBase(models.Model):
    class Meta:
        abstract = True

    count = models.PositiveIntegerField(
            default=0,
            editable=False,
            help_text=_("Total number of items ever added"))


class AutoScopedNumberField(models.PositiveIntegerField):
    """
    Field that allows positive integers counting numbers.
    """
    def __init__(self, *a, **k):
        k.setdefault('editable', False)
        models.PositiveIntegerField.__init__(self, *a, **k)

    def pre_save(self, instance, add):
        if add:
            val = instance.counted_generate_new_number(instance)
            setattr(instance, self.attname, val)
            return val
        else:
            # Otherwise just fall through
            return super(AutoScopedNumberField, self).pre_save(instance, add)


class CountedBase(models.Model):
    class Meta:
        abstract = True

    number = AutoScopedNumberField(db_index=True)

    @staticmethod
    def unique_together(parent):
        return ('number', parent)

    @classmethod
    def counted_generate_new_number(cls, instance):
        """
        Returns next available number for this CountedBase, within given scope

        (Note: Does not re-use numbers, even if something gets deleted. Also,
        starts counting at 1.)
        """
        parent = getattr(instance, cls.COUNTED_SCOPE)
        kwds = { cls.COUNTED_SCOPE: parent }
        result = cls.objects.filter(**kwds).aggregate(Max('number'))
        new_number = (result['number__max'] or 0) + 1
        return new_number


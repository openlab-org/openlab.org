# django
from django.utils.translation import ugettext as _
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.http import Http404

# third party
from cities_light.models import Country, Region, City

# first party
from openlab.core.generic_views import ViewInfo

class CountryListBase(ViewInfo):
    template_basename = "countrylist"
    breadcrumb = _('By country')
    template_interfix = "browse/"

    def get_context_data(self, request):
        countries = Country.objects.all()
        nouns = "%ss" % self.noun
        c = {
                'countries': countries,
                'model_class': self.model_class,
                'nouns': nouns,
                'noun': self.noun,
            }

        return c



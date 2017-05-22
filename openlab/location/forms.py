from django_select2 import AutoModelSelect2Field, HeavySelect2ChoiceField
from cities_light.models import Country, Region, City

from .views import AnyLocationSearch


class CLSelectField(AutoModelSelect2Field):
    search_fields = ['name__icontains']

class RegionSelectField(CLSelectField):
    queryset = Region.objects

class CountrySelectField(CLSelectField):
    queryset = Country.objects

class CitySelectField(CLSelectField):
    queryset = City.objects


class AnyLocationField(HeavySelect2ChoiceField):
    # Searches for region, country, and city simultaneously
    empty_value = u''

    def __init__(self, *a, **k):
        k['data_view'] = "location_ajax_search"
        self._k = k
        self._a = a
        super(AnyLocationField, self).__init__(*a, **k)

    # Uses like "region:123"
    #def coerce_value(self, value):
    #    return from_any_format(value)

    def get_val_txt(self, obj):
        return str(obj)
    
    def apply_to_locatable(self, value, locatable):
        # Note: can optimize if I store the city, region, and country in the
        # data from the user, then just set the IDs
        value = value or ''
        model_name, _, id = value.partition(':')
        if model_name == 'city':
            city = City.objects.get(id=id)
            locatable.set_city(city)

        elif model_name == 'region':
            region = Region.objects.get(id=id)
            locatable.set_region(region)

        elif model_name == 'country':
            country = Country.objects.get(id=id)
            locatable.set_country(country)

        else:
            # Otherwise clear everything
            locatable.city = None
            locatable.region = None
            locatable.country = None

    def with_choices(self, locatable):
        """
        Returns a copy of self with the field filled out according to what
        locatable specified.
        """
        choices = []
        if locatable.city:
            choices = (('city:%i' % locatable.city_id, str(locatable.city)), )

        elif locatable.region:
            choices = (('region:%i' % locatable.region_id, str(locatable.region)), )

        elif locatable.country:
            choices = (('country:%i' % locatable.country_id, str(locatable.country)), )

        k = { 'choices': choices }

        if choices:
            k['initial'] = choices[0][0]

        return self._updated(**k)

    def _updated(self, *a, **k):
        k.update(self._k)
        a = self._a + a
        return AnyLocationField(*a, **k)



from django_select2 import Select2View
from cities_light.models import Country, Region, City, to_search
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator


def _relevance(original_term, original_item):
    # Makes a search for 'Rio Grande do Sul' return "Rio Grande do Sul, Brazil"
    # first before Brazil and various cities, and a search for Madison return
    # Madison, Wisconsin, USA first before either the state or the country.
    item = to_search(original_item)
    term = to_search(original_term)
    if term in item:
        return 50 - original_item.count(',') - item.index(term)
    return 0


PAGE_SIZE = 5
class AnyLocationSearch(Select2View):
    def check_all_permisssions(request, *a, **k):
        if not request.user.is_authenticated():
            raise PermissionDenied()

    def get_results(self, request, term, page, context):
        # search: This is where we will want to optimize

        #.order_by('population')
        cities = City.objects.filter(search_names__icontains=term
                    ).select_related('country', 'region')

        # 5 cities at a time
        paginator = Paginator(cities, PAGE_SIZE)
        page = paginator.page(page)

        cities = list(page.object_list)
        regions = [city.region for city in cities]
        countries = [city.country for country in cities]
        results = []

        for country in countries:
            t = ('country:%i' % country.id, str(country))
            if t not in results:
                results.append(t)

        for region in regions:
            t = ('region:%i' % region.id, str(region))
            if t not in results:
                results.append(t)

        for city in cities:
            t = ('city:%i' % city.id, str(city))
            results.append(t)

        # Order by relevance
        results.sort(key=lambda a: -_relevance(term, a[1]))

        #       err      has_more       results
        return ('nil', page.has_next(), results)


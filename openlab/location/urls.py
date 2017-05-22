from django.conf.urls import url
from .views import AnyLocationSearch

urlpatterns = [
    url(r'^ajax/location/search/$', AnyLocationSearch.as_view(), name="location_ajax_search"),
]

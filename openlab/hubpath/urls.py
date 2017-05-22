from django.conf.urls import url
from .views import team_or_user

urlpatterns = [
    # Check for team or user style hubpaths
    url(r'^(?P<hubpath>[\w\._-]+)/?$', team_or_user),
]

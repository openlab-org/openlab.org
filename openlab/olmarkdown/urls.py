from django.conf.urls import url
from openlab.olmarkdown.views import preview
urlpatterns = [
    url(r'^ajax/preview/(?P<context_type>\w+)/(?P<context_id>\d+)/$',
        preview, {}, "olmarkdown_preview"),
]

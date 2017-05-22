from django.conf.urls import url
from openlab.release.views import project_preview

urlpatterns = [
    url(r'^ajax/preview/project/(?P<project_id>\d+)/$', project_preview, {}, "project_release_preview"),
]

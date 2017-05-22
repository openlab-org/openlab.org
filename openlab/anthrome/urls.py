from django.conf.urls import url
from openlab.anthrome.views import showcase, anthrome

urlpatterns = [
    url(r'^/?$', showcase, {}, "showcase"),
    url(r'^(?P<slug>[\w_-]+)/$', anthrome, {}, "anthrome"),
]

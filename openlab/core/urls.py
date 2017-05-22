from django.conf.urls import url
from openlab.core.views import press_kit, code

urlpatterns = [
    url(r'^press-kit/$', press_kit, {}, "press_kit"),
    url(r'^contribute/code/$', code, {}, "about_code_repos"),
]

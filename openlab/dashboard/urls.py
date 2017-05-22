from django.conf.urls import url
from openlab.dashboard.views import dashboard

urlpatterns = [
    # This URL is really never used, this just provides reverse for root
    url(r'^/?$', dashboard, {}, 'dashboard'),
]

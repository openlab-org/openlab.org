from django.conf.urls import url
from openlab.newsletter import views

urlpatterns = [
    # Post details
    url(r'^subscribe/openlab-announcements/$',
        views.global_subscribe_endpoint, {}, 'newsletter_global_subscribe'),
    url(r'^subscribe/(?P<content_type>[\w-]+)/(?P<content_id>[\w-]+)/$',
        views.subscribe_endpoint, {}, 'newsletter_subscribe_endpoint'),
    url(r'^instant-unsubscribe/$',
        views.unsubscribe, {}, 'newsletter_one_click_unsubscribe'),
]

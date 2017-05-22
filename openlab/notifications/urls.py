from django.conf.urls import url
from openlab.notifications.views import all, ajax_mark_read, test_view_email

urlpatterns = [
    url(r'^$', all, {}, name="notifications_all"),
    url(r'^ajax/mark-read/$', ajax_mark_read, {}, name="notifications_ajax_mark_read"),
    url(r'^__test__/email/$', test_view_email),
    url(r'^__test__/email/(?P<use_plaintext>pt)$', test_view_email),
]

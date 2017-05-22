from django.conf.urls import url
from openlab.discussion.views import view_thread

urlpatterns = [
    url(r'^(?P<thread_id>\d+)/$', view_thread, name="discussion_view_thread"),
]

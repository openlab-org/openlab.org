from django.conf.urls import url

from django.contrib.auth.views import login, logout

from openlab.core.generic_views import url_helper as u

from . import views
from .models import USERNAME_REGEXP
USER_PATH = r'^(?P<username>%s)' % USERNAME_REGEXP

urlpatterns = [
    # Registration is disabled
    #url(r'^accounts/', include('registration.backends.default.urls')),
    url(r'^login/$', login, {'template_name': 'accounts/login.html'}, name='auth_login'),
    url(r'^logout/$', logout, {'template_name': 'accounts/logout.html'}, name='auth_logout'),

    # Users
    # TODO: Remove this line, but replace all user_profile in templates
    url(USER_PATH+'/$', views.UserViewProfile.as_view(), {}, 'user_profile'),
    u(USER_PATH+'/$', views.UserViewProfile),
    u(USER_PATH+'/activity/$', views.UserViewActivity),
    u(USER_PATH+'/edit/$', views.UserEdit),
    u(USER_PATH+'/followers/$', views.UserViewFollowers),
    u(USER_PATH+'/edit/email/$', views.UserEditEmail),
    u(USER_PATH+'/edit/notifications/$', views.UserEditNotifications),
    u(USER_PATH+'/edit/password/$', views.UserEditPassword),
    u(USER_PATH+'/edit/delete/$', views.UserEditDelete),
    #u(USER_PATH+'/$', views.UserViewProfile),
]



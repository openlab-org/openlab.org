from django.conf.urls import url

from openlab.core.generic_views import url_helper as u

from . import views

TEAM_REGEXP = r'^(?P<slug>[\w-]+)/'

urlpatterns = [
    # List view
    #url(r'^$', views.TeamList.as_view(), {}, views.TeamList.url_name),
    u(r'^$', views.TeamList),
    u(r'^(?P<tab>[a-z][a-z][a-z]+)$', views.TeamList, url_name_suffix="_tab"),
    u(r'^countries/$', views.TeamCountryList),
    u(r'^(?P<country>[a-z][a-z])/$', views.TeamList),
    u(r'^(?P<country>[a-z][a-z])/(?P<region>[\w-]+)/$', views.TeamList),
    u(r'^(?P<country>[a-z][a-z])/(?P<region>[\w-]+)/(?P<city>[\w-]+)/$', views.TeamList),

    u(r'^new/$', views.TeamCreate),

    u(TEAM_REGEXP+'$', views.TeamView),
    u(TEAM_REGEXP+'activity/$', views.TeamViewActivity),
    u(TEAM_REGEXP+'followers/$', views.TeamViewFollowers),
    u(TEAM_REGEXP+'members/$', views.TeamViewMembers),
    u(TEAM_REGEXP+'gallery/$', views.TeamViewGallery),
    u(TEAM_REGEXP+'gallery/(?P<photo_id>\d+)/$', views.TeamViewPhoto),

    # Manage pages
    u(TEAM_REGEXP+'manage/edit/$', views.TeamManageEdit),
    u(TEAM_REGEXP+'manage/members/$', views.TeamManageMembers),
    u(TEAM_REGEXP+'manage/gallery/$', views.TeamManageGallery),
    u(TEAM_REGEXP+'manage/gallery/edit/$', views.TeamManageGalleryEdit),

    #url(r'^$', 'index', {}, "team_list"),
    #(r'^edit/(?P<team_slug>[\w-]+)/$',   'edit_team', {}, 'team_edit'),

    #(r'^new/$',                          'create_team', {}, 'team_new'),
    ###########################
]

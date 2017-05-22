from django.conf.urls import url
from openlab.core.generic_views import url_helper as u
from . import views

PROJECT_PATH = r'^(?P<hubpath>[\w-]+/[\w-]+)'
PROJECT_ACTION_PREFIX = r'^(?P<hubpath>[\w-]+/[\w-]+)'

urlpatterns = [
    ###########################
    # AJAX upload
    #url(r'ajax-upload$', 'import_uploader', name="project_ajax_upload"),


    ###########################
    # Index


    ###########################
    # Index
    #url(r'^$', views.TeamList.as_view(), {}, views.TeamList.url_name),
    u(r'^projects/$', views.ProjectList),
    u(r'^projects/(?P<tab>[a-z][a-z][a-z]+)$', views.ProjectList, url_name_suffix="_tab"),
    u(r'^projects/countries/$', views.ProjectCountryList),
    u(r'^projects/(?P<country>[a-z][a-z])/$', views.ProjectList),
    u(r'^projects/(?P<country>[a-z][a-z])/(?P<region>[\w-]+)/$', views.ProjectList),
    u(r'^projects/(?P<country>[a-z][a-z])/(?P<region>[\w-]+)/(?P<city>[\w-]+)/$', views.ProjectList),
    u(r'^(?P<project_namespace>[\w._-]+)/new/$', views.ProjectCreate),

    # Bare project view - this either displays release or redirects to view files
    url(PROJECT_PATH+'/$', views.project_release, {}, 'project'),
    # todo make file counted

    # Individual tabs
    u(PROJECT_PATH+'/files/$', views.ProjectViewFiles),
    u(PROJECT_PATH+'/files/(?P<file_id>\d+)/$', views.ProjectViewFile),
    u(PROJECT_PATH+'/details/$', views.ProjectViewOverview),
    u(PROJECT_PATH+'/activity/$', views.ProjectViewActivity),
    u(PROJECT_PATH+'/activity/revision/(?P<revision_number>\d+)/$', views.ProjectViewRevision),
    u(PROJECT_PATH+'/followers/$', views.ProjectViewFollowers),
    u(PROJECT_PATH+'/contributors/$', views.ProjectViewMembers),
    u(PROJECT_PATH+'/forks/$', views.ProjectViewForks),
    u(PROJECT_PATH+'/discussions/$', views.ProjectViewDiscussions),
    u(PROJECT_PATH+'/discussions/(?P<thread_id>\d+)/$', views.ProjectViewThread),

    ###########################
    # Update
    u(PROJECT_PATH+'/update/$', views.ProjectUpdate),

    # Revision endpoints
    url('^_project-u/delete/file/(?P<file_id>\d+)$', views.project_update_delete_file, {}, 'project_update_delete_file'),
    url('^_project-u/rename/file/$', views.project_update_rename_file, {}, 'project_update_rename_file'),
    url('^_project-u/delete/revision/(?P<revision_id>\d+)$', views.project_update_delete_revision, {}, 'project_update_delete_revision'),
    url('^_project-u/complete/(?P<revision_id>\d+)$', views.project_update_revision_complete, {}, 'project_update_revision_complete'),

    ###########################
    # Wiki stuff
    u(PROJECT_PATH+'/wiki/$', views.ProjectViewWiki),
    u(PROJECT_PATH+'/wiki/(?P<pageslug>[\w._-]+)/$', views.ProjectViewWiki),
    u(PROJECT_PATH+'/wiki/(?P<pageslug>[\w._-]+)/edit/$', views.ProjectEditWiki),
    u(PROJECT_PATH+'/wiki/(?P<pageslug>[\w._-]+)/history/$', views.ProjectEditHistoryWiki),

    ###########################
    # PHOTO Stuff
    # todo make counted
    u(PROJECT_PATH+'/gallery/$', views.ProjectViewGallery),
    u(PROJECT_PATH+'/gallery/(?P<photo_id>\d+)/$', views.ProjectViewPhoto),

    ###########################
    # Manage pages
    u(PROJECT_PATH+'/manage/files/$', views.ProjectManageFiles),
    u(PROJECT_PATH+'/manage/files/details/$', views.ProjectManageFilesEdit),
    u(PROJECT_PATH+'/manage/dependencies/$', views.ProjectManageDependencies),
    u(PROJECT_PATH+'/manage/edit/$', views.ProjectManageEdit),
    u(PROJECT_PATH+'/manage/access/$', views.ProjectManageMembers),
    u(PROJECT_PATH+'/manage/gallery/$', views.ProjectManageGallery),
    u(PROJECT_PATH+'/manage/wiki/$', views.ProjectManageWiki),
    u(PROJECT_PATH+'/manage/gallery/edit/$', views.ProjectManageGalleryEdit),
    u(PROJECT_PATH+'/manage/releases/$', views.ProjectManageReleases),
    u(PROJECT_PATH+'/manage/releases/new/$', views.ProjectManageReleasesNew),
    u(PROJECT_PATH+'/manage/releases/edit/(?P<version>[\w._-]+)/$', views.ProjectManageReleasesEdit),
]

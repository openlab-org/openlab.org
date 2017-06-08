from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views

from openlab.core.views import index as core_index
from openlab.core.views import press_kit as core_press_kit
from openlab.core.views import site_credits as core_site_credits

urlpatterns = [
    # User management
    url(r'^users/', include('openlab.users.urls', namespace='users')),
    url(r'^accounts/', include('allauth.urls')),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),

    # For logged out users: show anthrome showcase
    # For logged in users: show dashboard
    url(r'^$', core_index),
    url(r'^site-credits/', core_site_credits, {}, 'core_site_credits'),
    url(r'^press-kit/', core_press_kit, {}, 'core_press_kit'),

    # First, include anthrome's showcase
    url(r'^planet/', include('openlab.anthrome.urls')),

    # First, include anthrome's showcase
    url(r'^dashboard/', include('openlab.dashboard.urls')),

    # First misc core urls can be accessed here too
    url(r'^misc/', include('openlab.core.urls')),
    url(r'^activity/', include('actstream.urls')),

    # User profile stuff
    url(r'^user/', include('openlab.accounts.urls')),

    # notifications stuff
    url(r'^notifications/', include('openlab.notifications.urls')),

    # Built in auth urls, disabled
    #url(r'^account/', include(django.contrib.auth.urls)),

    # News
    url(r'^newsletter/', include('openlab.newsletter.urls')),

    # Teams
    url(r'^people/', include('openlab.team.urls')),

    # Discussion
    url(r'^discuss/', include('openlab.discussion.urls')),

    # misc gallery views
    url(r'^gallery/', include('openlab.gallery.urls')),

    ##### ##### #####
    # AJAX stuff
    url(r'^olmarkdown/', include('openlab.olmarkdown.urls')),
    url(r'^location/', include('openlab.location.urls')),
    url(r'^release/', include('openlab.release.urls')),
    url(r'^select2/', include('django_select2.urls')), # Select 2 URLs
    ##### ##### #####

    # NOTE: v- hardcoded in base.html
    url(r'^contact/', include('contact_form.urls')),

    #########
    # Project pages --- include directly based on slug
    url(r'^', include('openlab.project.urls')),

    # FINALLY, look for ANY hubpath
    url(r'^', include('openlab.hubpath.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

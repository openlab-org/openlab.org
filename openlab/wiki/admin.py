import reversion
from django.contrib import admin

from .models import WikiSite, WikiPage

class WikiPageAdmin(reversion.admin.VersionAdmin):
    list_display = ('title',)
    model = WikiPage

admin.site.register(WikiPage, WikiPageAdmin)

class WikiSiteAdmin(reversion.admin.VersionAdmin):
    list_display = ('id',)
    model = WikiSite

admin.site.register(WikiSite, WikiSiteAdmin)


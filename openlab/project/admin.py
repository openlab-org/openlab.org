import reversion
from django.contrib import admin

from .models import Project

class ProjectAdmin(reversion.admin.VersionAdmin):
    list_display = ('title', 'user')
    model = Project
admin.site.register(Project, ProjectAdmin)

import reversion
from django.contrib import admin

from .models import FileModel, Project

class ProjectAdmin(reversion.admin.VersionAdmin):
    list_display = ('title', 'user')
    model = Project

admin.site.register(Project, ProjectAdmin)

# Use standard model admin for FileModel, use custom 
class FileModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'size', 'license')
    model = FileModel

admin.site.register(FileModel, FileModelAdmin)


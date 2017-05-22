from .models import *
from django.contrib import admin

from django.core.exceptions import ValidationError

class FeaturedProjectAdmin(admin.ModelAdmin):
    exclude = ('user',)
    list_display = ('active', 'date_featured', 'date_last_featured', 'user', 'project')

    def save_model(self, request, obj, form, change):
        # Auto add the last person
        #if not obj.project.is_featurable():
        #    raise ValidationError("Cannot save using this project, it's not completed enough.")
        obj.user = request.user
        obj.save()

admin.site.register(FeaturedProject, FeaturedProjectAdmin)


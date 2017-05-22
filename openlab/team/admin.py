from django.contrib import admin

from .models import Team

class TeamAdmin(admin.ModelAdmin):
    list_display = ('title', 'user')
    model = Team

admin.site.register(Team, TeamAdmin)



from django import forms

from django_select2 import AutoModelSelect2Field 
from core.forms import InfoBaseForm

from .models import Team


class CreateTeamForm(InfoBaseForm):
    name = "Team"
    class Meta:
        fields = InfoBaseForm._fields
        widgets = InfoBaseForm._widgets
        model = Team

    def copy_from(self, instance):
        return instance.user


class EditTeamForm(CreateTeamForm):
    class Meta:
        fields = InfoBaseForm._edit_fields
        widgets = InfoBaseForm._edit_widgets
        model = Team


class SelectTeamField(AutoModelSelect2Field):
    queryset = Team.objects
    search_fields = ['title__icontains', 'slug__icontains']


class TeamSelectForm(forms.Form):
    team = SelectTeamField()

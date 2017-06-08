from django import forms
from django.utils.translation import ugettext as _

from core.forms import InfoBaseForm, PhotoSelect2Widget

from .models import Project

from django_select2.widgets import *
from django_select2 import AutoModelSelect2Field
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout


class CreateProjectForm(InfoBaseForm):
    name = "Project"
    class Meta:
        fields = ('git_url',) + InfoBaseForm._fields + ('license',)
        widgets = InfoBaseForm._widgets
        widgets['license'] = forms.RadioSelect
        model = Project

    def copy_from(self, instance):
        # Guess location from the following try order
        return instance.team or instance.user or instance.team.user


class EditProjectForm(CreateProjectForm):
    class Meta:
        fields = InfoBaseForm._edit_fields + ('license',)
        widgets = InfoBaseForm._edit_widgets
        widgets['license'] = forms.RadioSelect
        model = Project


class SelectProjectField(AutoModelSelect2Field):
    queryset = Project.objects
    search_fields = ['title__icontains', 'slug__icontains']


class AddDependencyForm(forms.Form):
    project_to_add = SelectProjectField(
            label=_('Add'),
            help_text=_('Search for a project to add as a '
                '"component dependency" for this project.'))

    def __init__(self, *a, **k):
        super(AddDependencyForm, self).__init__(*a, **k)
        self.helper = FormHelper()
        self.helper.form_tag = False

        # Horizontal form
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'


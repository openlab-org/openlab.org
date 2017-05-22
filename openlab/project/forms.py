from django import forms
from django.utils.translation import ugettext as _

from core.forms import InfoBaseForm, PhotoSelect2Widget

from .models import Project, FileModel, Revision

from django_select2.widgets import *
from django_select2 import AutoModelSelect2Field
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout


class CreateProjectForm(InfoBaseForm):
    name = "Project"
    class Meta:
        fields = InfoBaseForm._fields + ('license',)
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


class EditFileForm(forms.ModelForm):
    class Meta:
        fields = ('title', 'description', 'file_license', 'credits', 'photo',)
        widgets = {
                'license': forms.RadioSelect,
                'photo': PhotoSelect2Widget,
            }

        model = FileModel

    def __init__(self, *a, **k):
        super(EditFileForm, self).__init__(*a, **k)
        self.helper = FormHelper()
        self.helper.form_tag = False


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


class RevisionForm(forms.ModelForm):
    class Meta:
        fields = ('summary', 'changes',)
        model = Revision

    def __init__(self, *a, **k):
        super(RevisionForm, self).__init__(*a, **k)



class RenameFileForm(forms.ModelForm):
    """
    For renaming or moving files
    """
    class Meta:
        fields = ('filename', 'folder', 'replaces', 'removed')
        model = FileModel

    def __init__(self, *a, **k):
        tip_files = k.pop('tip_files')

        super(RenameFileForm, self).__init__(*a, **k)
        self.helper = FormHelper()
        self.helper.form_tag = False

        # Horizontal form
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.fields['replaces'].queryset = tip_files



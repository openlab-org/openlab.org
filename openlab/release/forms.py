import json

# django
from django import forms

# third party
# from django_select2.widgets import *
from crispy_forms.helper import FormHelper

# local
from .models import Release
from .util import auto_version


# New edit release form
class EditReleaseMediaForm(forms.ModelForm):
    media = forms.HiddenInput()

    class Meta:
        #fields = ('license', 'version',
        fields = ('version', 'summary', 'text', 'notes')
        model = Release

    def __init__(self, *a, **k):
        project = k.pop('project', None)
        previous = k.pop('previous', None)

        k.setdefault('initial', {})

        k['initial']['summary'] = project.summary
        k['initial']['version'] = auto_version(previous)

        super(EditReleaseMediaForm, self).__init__(*a, **k)
        self.helper = FormHelper()
        self.helper.form_tag = None
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'

    def get_media_data(self, post):
        files = post.get('files')

# Old release form
class EditReleaseForm(forms.ModelForm):
    class Meta:
        fields = ('license', 'version', 'components',
                  'summary', 'text', 'notes')

        widgets = {
            'components': forms.HiddenInput,
        }
        model = Release

    def __init__(self, *a, **k):
        project = k.pop('project', None)
        previous = k.pop('previous', None)

        k.setdefault('initial', {})
        if project:
            k['initial']['summary'] = project.summary

        k['initial']['version'] = auto_version(previous)

        # Get revisions between this one and prev to autogenerate change notes
        #k['initial']['notes'] = auto_notes(project, previous)

        super(EditReleaseForm, self).__init__(*a, **k)
        self.helper = FormHelper()
        #self.helper.form_class = 'form-horizontal'
        self.helper.form_tag = None
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'

    def clean_components(self):
        data_s = self.cleaned_data['components']
        try:
            data = json.loads(data_s)
        except ValueError:
            raise forms.ValidationError("Invalid JSON")
        return data


from urllib.parse import urlparse, urlencode

from django import forms
from django.utils.translation import ugettext as _

from core.forms import InfoBaseForm

from django_select2 import AutoModelSelect2Field
from crispy_forms.helper import FormHelper

from .models import Project
from .view_helpers import github_get_repo_commits, beautify_repo_name


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


class PreCreateForm(forms.Form):
    '''
    Non-crispy form (to have more control) for the initial experience of
    "importing" a project from an existing source (and, eventually, creating
    one from scratch utilizing OL's flat file system)
    '''
    git_url = forms.URLField()

    GET_FIELDS = [
        'git_url',
        'topics',
        'summary',
        'slug',
        'title',
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_querystring(self):
        # TODO Add validation to custom form field, GitHubURLField
        git_url = self.cleaned_data['git_url']
        path = urlparse(git_url).path.strip('/')
        username, reponame = path.split('/')
        repo_info = github_get_repo_commits(username, reponame)
        data = {}
        data['git_url'] = repo_info.get('clone_url', git_url)
        data['topics'] = ', '.join(repo_info.get('topics', []))
        data['summary'] = repo_info.get('description', '')
        data['slug'] = repo_info.get('name', '')
        data['title'] = beautify_repo_name(repo_info.get('name', ''))
        return urlencode(data)

    @classmethod
    def get_initial(cls, get_data):
        data = {}
        for key in cls.GET_FIELDS:
            if key in get_data:
                data[key] = get_data[key]
        return data


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
        super().__init__(*a, **k)
        self.helper = FormHelper()
        self.helper.form_tag = False

        # Horizontal form
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'


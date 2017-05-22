
from django import forms

from django.utils.translation import ugettext as _
from core.forms import InfoBaseForm, PhotoSelect2Widget

from .models import WikiSite, WikiPage
from django.utils import formats
from django_select2.widgets import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
import reversion


class ManageWikiForm(forms.ModelForm):
    class Meta:
        fields = ('public_editable', 'is_disabled', 'is_public')
        model = WikiSite

    def __init__(self, *a, **k):
        instance = k.get('instance')

        super(ManageWikiForm, self).__init__(*a, **k)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))
        if instance and instance.is_disabled:
            del self.fields['public_editable']
            del self.fields['is_public']


class EditPageForm(forms.ModelForm):
    class Meta:
        fields = ('title', 'text')
        model = WikiPage

    comments = forms.CharField(
            required=False,
            label=_("Edit summary"),
            help_text=_("Briefly describe the changes you have made"))


    def __init__(self, *a, **k):
        #instance = k.get('instance')

        super(EditPageForm, self).__init__(*a, **k)

        self.fields['text'].widget.attrs = {'data-olmarkdown': "wiki"}

        self.helper = FormHelper()

        # Set name
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))

        # Horizontal form
        #self.helper.form_class = 'form-horizontal'
        #self.helper.label_class = 'col-lg-2'
        #self.helper.field_class = 'col-lg-10'


class PageHistoryForm(forms.Form):
    revision = forms.ChoiceField(
            widget=forms.RadioSelect,
            label=_("Revision list"),
            help_text=_("To revert to an earlier version, first select "
                        "it, then submit this form."))

    def format_version(self, v):
        r = v.revision
        dt = formats.date_format(r.date_created, "SHORT_DATETIME_FORMAT")
        return u"%s - %s [Comment: %s]" % (dt, r.user.username, r.comment or _("None"))

    def __init__(self, *a, **k):
        instance = k.pop('instance')

        super(PageHistoryForm, self).__init__(*a, **k)

        # Build a list of all previous versions, latest versions first:
        self.version_list = reversion.get_for_object(instance)
        self.fields['revision'].choices = [(i, self.format_version(v)) for i, v
                                            in enumerate(self.version_list)]

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Revert to selected'))


    def get_version(self):
        num = int(self.cleaned_data['revision'])
        version = self.version_list[num]
        return version


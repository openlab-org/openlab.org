# python
import json

# django
from django import forms
from django.utils.translation import ugettext as _

# third party
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, ButtonHolder

# first party
from openlab.core.forms import TagField

# local
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        fields = ('text',)
        model = Message

    def __init__(self, *a, **k):
        thread_exists = k.pop('thread_exists', False)
        users = k.pop('users', [])
        super(MessageForm, self).__init__(*a, **k)

        self.fields['text'].widget.attrs = { 'data-olmarkdown': "message" }

        if thread_exists:
            u_attr = json.dumps([u.username for u in users])
            self.fields['text'].widget.attrs['data-users'] = u_attr

        # Sets up form
        self.helper = FormHelper()
        submit_text = self.submit_text(thread_exists)

        layout = list(self.my_field_order) + [
            ButtonHolder( Submit('submit', submit_text, css_class='btn-block'))]

        self.helper.layout = Layout(*layout)

    def submit_text(self, thread_exists):
        "Text for submit button"
        # get rid of distraction since its obvious
        self.fields['text'].label = u""
        self.fields['text'].help_text = None
        return _('Post reply' if thread_exists else 'Post new comment')

    def save_to_thread(self, thread):
        # Trigger update in last commented, and/or create new 
        thread.save()

    @property
    def my_field_order(self):
        return self.Meta.fields


class NewThreadForm(MessageForm):
    # Same thing as message form but also has title for thread
    title = forms.CharField(help_text=_("A title for the topic of discussion"))
    tags = TagField(required=False)

    def submit_text(self, thread_exists):
        # Horizontal form
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-1'
        self.helper.field_class = 'col-lg-11'

        return _('Create new discussion')

    def save_to_thread(self, thread):
        thread.title = self.cleaned_data['title']
        # Create new thread
        thread.save()

        # populate tags
        result = self.cleaned_data['tags']
        thread.tags.set(*result)

    @property
    def my_field_order(self):
        return ('title', 'text', 'tags',)


from django import forms

from .models import Photo

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout


class EditPhotoForm(forms.ModelForm):
    class Meta:
        fields = ('title', 'description',)
        model = Photo

    def __init__(self, *a, **k):
        super(EditPhotoForm, self).__init__(*a, **k)
        self.helper = FormHelper()
        self.helper.form_tag = False



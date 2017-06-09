# python
import re

# django
from django import forms
from django.core.paginator import Paginator
from django.template.defaultfilters import slugify

# third party
from django_select2 import AutoSelect2TagField
from django_select2.widgets import Select2Widget
#from django_select2.util import JSFunction
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from taggit.models import Tag

# first party
from openlab.gallery.models import Photo

#from location.forms import RegionSelectField, CountrySelectField, CitySelectField
from openlab.location.forms import AnyLocationField

# local
from .models import InfoBaseModel


PAGE_SIZE = 5
class TagField(AutoSelect2TagField):
    """
    This overrides some core functionality from what we inherit from, in order
    to let the taggit-manager handle all the model creation / destuction using
    its special methods instead of doing it by hand.
    """
    @staticmethod
    def clean_tag(tag):
        # Normalizes tags
        return slugify(tag.lower().strip()).replace('--', '-').strip('-')

    def coerce_value(self, value):
        # XXX ugh this is an awful hack, i am stupid
        MYSTERIOUS_CRAP = ' tagged with '
        if MYSTERIOUS_CRAP in value:
            _, _, real_value = value.partition(MYSTERIOUS_CRAP)
            return self.clean_tag(real_value)

        if isinstance(value, str):
            return self.clean_tag(value)
        else:
            return self.clean_tag(value.name)

    #def to_python(self, value):
    #    if not value: return []
    #    return list(set([self.clean_tag(tag) for tag in value]))

    def security_check(self, request, *a, **k):
        return request.user.is_authenticated()

    def validate_value(self, value):
        return isinstance(value, str)

    def get_val_txt(self, value):
        return self.coerce_value(value)

    def get_results(self, request, term, page, context):

        # @search
        # Search for tags
        qs = Tag.objects.filter(name__icontains=term)

        # get the current page
        paginator = Paginator(qs, PAGE_SIZE)
        page = paginator.page(page)

        # turn it into a list of choice like things
        tags = list(map(str, page.object_list))
        choices = list(zip(tags, tags))
        return ('nil', page.has_next(), choices, )


class PhotoSelect2Widget(Select2Widget):
    """
    Select2Widget for selecting photos from a list
    """
    DELIM = " | "
    FORMAT_JS = """
            var split = function (state) {
                var DELIM = '%s';
                var s = state.text.split(DELIM, 1);
                var url = s.shift();
                var desc = s.join(DELIM);
                return {url: url, desc: desc};
            };

            var photo_selection_format = function (state) {
                if (!state.id) {
                    return 'None';
                }
                return "Photo selected " + split(state).desc;
                return "Photo " + state.id + " " + split(state).desc;
            };

            var photo_result_format = function (state) {
                var s = split(state);
                if (!state.id) {
                    return '<div class="well"><strong>None</strong></div>';
                }
                return '<div class="photo-option">'+
                        '<img class="img-rounded" src="'+
                            s.url+'" />'+s.desc+'</div>';
            };
        """.replace('    ', '').replace("\n adjf", ' ') % DELIM

    def __init__(self, *a, **k):
        super(PhotoSelect2Widget, self).__init__(*a, **k)

    def init_options(self):
        super(PhotoSelect2Widget, self).init_options()
        # TODO: need to replace this, possibly replace SELECT2 in general
        #self.options['formatSelection'] = JSFunction('photo_selection_format')
        #self.options['formatResult'] = JSFunction('photo_result_format')

    def render_inner_js_code(self, id_, *args):
        s = PhotoSelect2Widget.FORMAT_JS
        s += super(PhotoSelect2Widget, self).render_inner_js_code(id_, *args)
        return s

class AutoField(forms.ChoiceField):
    def __init__(self, *a, **k):
        from_field = k['from_field']
        attrs = {
                'class':         'auto-field',
                'data-target':    from_field,
                'data-operation': self.operation,
            }

        if self.allow_force:
            attrs['data-allow-force'] = 'true'

        k['widget'] = forms.TextInput(attrs=attrs)

        del k['from_field']
        super(AutoField, self).__init__(*a, **k)


class SlugField(AutoField):
    regexp = re.compile('^[\w-]+$')
    _err = {
            'invalid': "Invalid slug. Slugs look like 'words-separated-by-dashes",
        }
    operation = 'slug'
    allow_force = True

    def to_python(self, value):
        if not value or value.strip():
            return None
        if not regexp.match(value):
            raise ValidationError("Invalid slug.", _err['invalid'])
        return value


class InfoBaseForm(forms.ModelForm):
    """
    Don't instantiate directly, just useful to derive from
    """
    _fields = ('title', 'slug', 'summary', 'location',)
    _edit_fields = ('title', 'summary', 'location', 'photo', 'tags')
    _widgets = {
            'slug': forms.TextInput(
                    attrs={
                        'data-autofield': 'title',
                    }
                )
        }

    location = AnyLocationField(required=False)
    #slug = SlugField(from_field='title')

    _edit_widgets = dict(_widgets)
    _edit_widgets.update(
            photo=PhotoSelect2Widget()
        )

    tags = TagField(required=False)

    def __init__(self, *a, **k):
        instance = k.get('instance')

        super(InfoBaseForm, self).__init__(*a, **k)

        #if self.fields.get('description'):
        #    self.fields['description'].widget.attrs = {'data-olmarkdown': "description"}

        self.helper = FormHelper()

        # Set name
        #self.helper.form_id = 'team_edit'
        self.helper.form_method = 'post'
        #self.helper.form_action = 'team_edit'
        self.helper.add_input(Submit('submit', 'Save'))

        # Horizontal form
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        if self.fields.get('photo'):
            # Populate 
            if self.instance and self.instance.gallery:
                # Can only select from gallery photos
                self.fields['photo'].queryset = self.instance.gallery.photos.all()
            else:
                # This happens if the gallery hasnt been made yet, so clear the
                # queryset
                self.fields['photo'].queryset = Photo.objects.none()

        if instance:
            # Prepopulate with initial location info
            new = self.fields['location'].with_choices(instance)
            self.fields['location'] = new

            # And with the current tags
            tags = list(map(str, instance.tags.all()))
            self.fields['tags'].initial = tags
            #self.cleaned_data['tags'] = tags

    def save(self, *a, **k):
        if self.instance and self.instance.id:
            # populate location
            self.after_save_setup()

        return super(InfoBaseForm, self).save(*a, **k)

    def after_save_setup(self):
        self.fields['location'].apply_to_locatable(
                    self.cleaned_data['location'],
                    self.instance)

        # populate tags
        result = self.cleaned_data['tags']
        self.instance.tags.set(*result)



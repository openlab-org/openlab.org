# django
from django.utils.safestring import mark_safe, mark_for_escaping
from django.utils.translation import ugettext as _
from openlab.users.models import User
from django import forms

# 3rd party
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div
from django_select2 import AutoModelSelect2Field

# 1st party
from openlab.notifications.models import new as new_notification

# local
from openlab.accounts.models import Profile

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name',
                'description',
                #'bio', 'interests',
                'plaintext_email', 'email_notification')

    first_name = forms.CharField(
                label=_("First name"), 
                required=False,
                help_text=_("Your real name. I know you have one..."))

    last_name = forms.CharField(
                label=_("Last name"),
                required=False)

    def __init__(self, *a, **k):
        super(EditProfileForm, self).__init__(*a, **k)
        self.helper = FormHelper()

        # Set name
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('action', 'Save'))
        self.helper.add_input(Submit('action', 'Cancel'))

        # Horizontal form
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        if 'instance' in k:
            self.fields['first_name'].initial = k['instance'].user.first_name
            self.fields['last_name'].initial = k['instance'].user.last_name

    def save(self, *a, **k):
        self.instance.user.first_name = self.cleaned_data['first_name']
        self.instance.user.last_name = self.cleaned_data['last_name']
        super(EditProfileForm, self).save(*a, **k)
        self.instance.user.save()


class _OnlyForm(forms.ModelForm):
    def __init__(self, *a, **k):
        k.setdefault('prefix', self._prefix)
        super(_OnlyForm, self).__init__(*a, **k)
        self.helper = FormHelper()

        # Horizontal form
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-10'

        self.helper.form_tag = False

class OnlyEditProfileForm(_OnlyForm):
    _prefix = "profile"
    class Meta:
        model = Profile
        fields = (
                    'description',
                    'prefered_name',
                    #'bio', 'interests'
                )

class _Base(forms.ModelForm):
    def __init__(self, *a, **k):
        super(_Base, self).__init__(*a, **k)
        self.helper = FormHelper()
        self.helper.label_class = 'col-lg-2' # Horizontal form
        self.helper.field_class = 'col-lg-10'

        # Set name
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('action', 'Save', css_class="btn btn-block btn-primary"))

        # Horizontal form
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'



class EditNotificationsUserForm(_OnlyForm):
    _prefix = 'user'
    class Meta:
        model = User
        fields = tuple()

class EditNotificationsForm(_OnlyForm):
    _prefix = 'profile'
    class Meta:
        model = Profile
        fields = ('plaintext_email', 'email_notification')


class EditEmailForm(_Base):
    class Meta:
        model = User
        fields = ('email', )


class OnlyEditUserForm(_OnlyForm):
    _prefix = "user"
    class Meta:
        model = User
        fields = ('first_name', 'last_name',)


class SelectUserField(AutoModelSelect2Field):
    queryset = User.objects
    search_fields = ['first_name__icontains', 'last_name__icontains', 'username__icontains']


class UserSelectForm(forms.Form):
    user = SelectUserField(label="")


def make_manage_user_forms_context(request, instance, field):
    form = UserSelectForm()

    def handle_post():
        if request.POST.get('delete'):
            user_id = int(request.POST['delete'])

            # @optimize makes an extra call
            user = User.objects.get(id=user_id)
            field.remove(user)
            return

        #####################
        # Now we see if its the user select form that was submitted
        if request.POST.get('submit') == 'add':
            # The add user form is being used

            form = UserSelectForm(request.POST)
            if form.is_valid():
                user = form.cleaned_data['user']
                # Add the user to the instance
                field.add(user)
                _send_notification(user, request.user, instance)
            return
        #####################


        #####################
        # Now we check if we are submitting an invitation
        #if request.POST.get('invite'):
        #    # The invite user form is being used!
        #    return
        #####################

    if request.method == "POST":
        handle_post()

    users = list(field.all())

    # Remove self from list display
    try:
        users.remove(request.user)
    except ValueError:
        # for some reason we aren't in our own team, huh
        pass

    return {
        'musers_forms': {
            'new_user': form,
            'users': users,
            'permission_options': [],
        }
    }

def _send_notification(user, from_user, instance):
    url = instance.get_absolute_url()
    name = from_user.profile.desired_name
    msg = u"%s added you as a contributor to %s" % (name, str(instance))
    new_notification(user, msg, url=url, actor=from_user, topic=instance)

def make_manage_user_access_forms_context(request, instance, kwargs, through_model):
    # XXX both this method and the above one are a giant mess and need
    # re-writing, maybe when we add an invite user feature
    form = UserSelectForm()

    def handle_post():
        if request.POST.get('delete'):
            user_id = int(request.POST['delete'])

            # @optimize makes an extra call
            user = User.objects.get(id=user_id)
            k2 = dict(kwargs)
            k2['user'] = user
            through_model.objects.filter(**k2).delete()
            return

        #####################
        # Now we see if its the user select form that was submitted
        if request.POST.get('submit') == 'add':
            # The add user form is being used

            form = UserSelectForm(request.POST)
            if form.is_valid():
                user = form.cleaned_data['user']
                # Add the user to the instance
                k2 = dict(kwargs)
                k2['user'] = user
                _send_notification(user, request.user, instance)
                through_model.objects.create(**k2)
            return
        #####################

    if request.method == "POST":
        handle_post()

    throughs = list(through_model.objects.filter(**kwargs))
    users = list(map(lambda t: t.user, throughs))

    # Remove self from display list, if shown
    try: users.remove(request.user)
    except ValueError: pass

    return {
        'musers_forms': {
            'new_user': form,
            'users': users,
            'permission_options': [],
        }
    }



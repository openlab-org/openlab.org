import hashlib

from django.db import models
from openlab.users.models import User
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse

from taggit.managers import TaggableManager

# 1st party
from openlab.gallery.models import Gallery, Photo
from openlab.location.models import LocatableBaseModel
from openlab.hubpath.models import HubPathBase
from openlab.olmarkdown.models import OLMarkdownBase

USERNAME_REGEXP = r'[\w\.-]+'


class Profile(LocatableBaseModel, OLMarkdownBase, HubPathBase):
    """model to represent additional information about users"""
    user = models.OneToOneField(User, related_name='profile')

    # Basic info
    description = models.TextField(
            default="", blank=True,
            help_text=_("Tell the community a bit about yourself!"),
            verbose_name=_("About me"))

    photo = models.ForeignKey(Photo,
                null=True, blank=True,
                help_text=_("So what do you look like?"))

    FIRST_LAST   = 'w' # western
    FIRST_LAST_I = 'i'
    FIRST        = 'f'
    USERNAME     = 'u'
    PREFERED_NAME_CHOICES = (
            (FIRST_LAST, '...first name then last name'),
            (FIRST_LAST_I, '...first name then last initial'),
            (FIRST, '...first name only'),
            (USERNAME, '...username only'),
        )

    prefered_name = models.CharField(max_length=1,
            choices=PREFERED_NAME_CHOICES,
            default=FIRST_LAST,
            help_text=_("We know how annoying it is when people call you by the"
                        "wrong name. So try to get the little things right."),
            verbose_name=_("Refer to me with my..."))

    plaintext_email = models.BooleanField(default=False,
            verbose_name=_("Plain text emails"),
            help_text=_("Send me only ugly emails."))

    email_notification = models.BooleanField(default=True,
            verbose_name=_("Enable email notifications"),
            help_text=_("You can disable email notifications altogether, but we promise we won't bug you."))


    # Just use tags for badges
    simple_badges = TaggableManager()
    def save(self, *a, **k):
        super(Profile, self).save(*a, **k)

        # Save to cache with every save
        self.save_cache()

    @property
    def badges(self):
        # If we later want to add more proper badges, using "badges" as a
        # placeholder
        return self.simple_badges.all()

    GRAVATAR_URL = "http://gravatar.com/avatar/%s?d=identicon%s"
    def gravatar(self, size=None):
        email = str(self.user.email).strip().lower()
        digest = hashlib.md5(email.encode('utf-8')).hexdigest()

        if size:
            size_str = '&s=%i' % size
        else:
            size_str = ''

        return self.GRAVATAR_URL % (digest, size_str)

    def avatar_url(self):
        #if self.photo and self.photo.preview_ready():
        #    return self.photo.preview_image_thumb
        return self.gravatar()

    def avatar_url_150(self):
        #if self.photo and self.photo.preview_ready():
        #    return self.photo.preview_image_thumb
        return self.gravatar(size=150)

    def get_absolute_url(self):
        return reverse('user_profile', args=(self.user.username,))

    @property
    def full_name(self):
        return u"%s %s" % (self.user.first_name, self.user.last_name)

    @property
    def desired_name(self):
        # A system of "fall backs"
        preferences = [self.user.username]
        first_name = self.user.last_name
        if self.prefered_name != self.USERNAME:
            if first_name:
                preferences.insert(0, self.user.first_name)

        if self.prefered_name == self.FIRST_LAST:
            preferences.insert(0, self.full_name)
        elif self.prefered_name == self.FIRST_LAST_I:
            last_name = self.user.last_name
            if last_name:
                last_i = u"%s %s." % (first_name, last_name[0].upper())
                preferences.insert(0, last_i)

        while preferences:
            top = preferences.pop(0)
            if top and top.strip():
                return top.strip()
        # should never, ever get here
        return self.user.username

    def __str__(self):
        return self.full_name

    def get_olmarkdown_source(self):
        """
        "Description" is the field we use for the source
        """
        return self.description

    def fetch_olmarkdown_context_object(self):
        """
        InfoBase objects generally should use themselves as the context.
        """
        return self




def create_default(user):
    Profile.objects.create(user=user, slug=user.username)

#######################################################################
## SIGNALS  ###########################################################
#######################################################################
def user_post_save(sender, instance, created, **kwargs):
    if created:
        create_default(instance)

models.signals.post_save.connect(user_post_save, sender=User)



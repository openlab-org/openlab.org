# django
from django.db import models
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# 3rd party
from taggit.managers import TaggableManager

# first party
from openlab.users.models import User
from openlab.olmarkdown.models import OLMarkdownBase
from openlab.counted.models import ScopeBase, CountedBase


class ThreadSubscription(models.Model):
    """
    Represents options for a subscription to the thread
    """
    user = models.ForeignKey(User)
    thread = models.ForeignKey('Thread')

    is_participant = models.BooleanField(default=True, db_index=True)
    is_email_subscription = models.BooleanField(default=True, db_index=True)
    last_viewed = models.DateTimeField(auto_now=True)


class Thread(ScopeBase):
    class Meta:
        get_latest_by = "last_edited"

    last_edited = models.DateTimeField(auto_now=True, db_index=True)
    creation_date = models.DateTimeField(auto_now_add=True, db_index=True)

    user = models.ForeignKey(User, null=True, blank=True,
        help_text=_("Thread starter."))

    is_private = models.BooleanField(default=False, db_index=True,
        help_text=_("If this thread is private to subscribers."))

    subscribers = models.ManyToManyField(User,
        related_name='thread_subscribers',
        help_text=_("Users who have participated in this thread."))

    # Discussable objects...
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    topic_object = GenericForeignKey()

    # Extra meta data for stand-alone threads
    title = models.CharField(
            help_text=_("Topic for the discussion thread."),
            verbose_name=_("Title"),
            max_length=255)

    tags = TaggableManager(
            help_text=_("Tags for the thread."))

    def is_visible_to(self, user):
        if not self.is_private:
            return True
        subs = self.subscribers.all()
        return user in subs


    def get_absolute_url(self):
        topic = self.topic_object
        if not topic:
            # An absolute thread URL, for things like private messages
            url = reverse('discussion_view_thread', args=(self.id,))
        else:
            # Normal discussion, comment section somewhere etc
            if hasattr(topic, "get_absolute_thread_url"):
                # Topic Object is something like a Project, can get individual
                # discussion URL
                url = topic.get_absolute_thread_url(self)
            else:
                # Topic Object is something like a photo or file
                url = topic.get_absolute_url()

        return url


class Message(OLMarkdownBase, CountedBase):
    COUNTED_SCOPE = 'thread'
    class Meta:
        unique_together = (CountedBase.unique_together('thread'), )
        index_together = (CountedBase.unique_together('thread'), )
        get_latest_by = "creation_date"

    thread = models.ForeignKey(Thread,
            related_name="messages",
            help_text=_("Parent thread"))

    user = models.ForeignKey(User)

    reply_to = models.ForeignKey('Message', related_name="replies",
            blank=True, null=True)

    last_edited = models.DateTimeField(auto_now=True)
    creation_date = models.DateTimeField(auto_now_add=True, db_index=True)

    is_edited = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False, db_index=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    text = models.TextField(
            verbose_name=_("Text"),
            help_text=_("Message text. <em>(Markdown syntax is available.)</em>"))

    plusones = models.ManyToManyField(User,
        related_name='message_plusones',
        help_text=_("Users who have +1'd this message."))

    def editable_by(self, user):
        if self.user == user:
            return True
        elif user.is_staff:
            return True
        return False


    def get_absolute_url(self):
        # Get thread URL
        url = self.thread.get_absolute_url()

        # add in hash number
        return "%s#m%i" % (url, self.id)


    def get_olmarkdown_source(self):
        """
        "Description" is the field we use for the source
        """
        return self.text


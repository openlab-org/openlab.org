from django.db import models

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from openlab.users.models import User


class Notification(models.Model):
    class Meta:
        get_latest_by = "-creation_date"

    PRIVATE = 40
    DIRECT = 30
    ADJACENT = 20
    FOLLOWING = 10
    RELEVANCE_CHOICES = [
        (PRIVATE, 'Private'),
        (DIRECT, 'Direct'),
        (ADJACENT, 'Adjacent'),
        (FOLLOWING, 'Following'),
    ]

    relevance = models.PositiveSmallIntegerField(
            choices=RELEVANCE_CHOICES, default=ADJACENT)

    user = models.ForeignKey(User)
    creation_date = models.DateTimeField(auto_now_add=True)
    #creation_date = models.DateTimeField(auto_now_add=True, db_index=True)
    message = models.CharField(max_length=255)

    # if another user's action generated this, then this user goes here
    actor = models.ForeignKey(User, null=True, blank=True,
                related_name="notifications_generated")

    # this notification was looked at, although not necessarily clicked
    read = models.BooleanField(default=False, 
        db_index=True,
        help_text="If its been read.")

    mailed = models.BooleanField(default=False, 
        db_index=True,
        help_text="if an email alert was sent for this notifiaction")

    # URL to go to, relative to this site
    url = models.CharField(max_length=255, null=True, blank=True)

    # Context, if applicable
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    topic_object = GenericForeignKey()

    def get_url(self):
        if self.url:
            return self.url
        topic = self.topic_object

        if topic and hasattr(topic, "get_absolute_url"):
            return self.topic_object.get_absolute_url()
        else:
            return None


    @classmethod
    def get_unsent(cls, user=None):
        """
        Returns mailable messages optionally filtered by user.
        """
        result = cls.objects.filter(mailed=False, read=False)

        if user:
            result = result.filter(user=user)
        result = result.select_related('user').order_by('user')

        return result


def new(user, message, actor=None, topic=None, url=None, context=None):
    n = Notification(user=user,
            message=message,
            actor=actor,
            url=(url or ""))

    if topic:
        n.topic_object = topic

    n.save()


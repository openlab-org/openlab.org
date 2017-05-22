# django
from django.db import models
from openlab.users.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Subscription(models.Model):
    class Meta:
        get_latest_by = "subscribe_date"

    def __str__(self):
        if self.user:
            return u"(%s) %s - %s" % (str(self.publish_date),
                    self.user, self.user.email_address)
        else:
            return u"(%s) %s" % (str(self.publish_date), self.email_address)

    subscribe_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, blank=True, null=True)
    email_address = models.EmailField(blank=True, null=True,
                                    max_length=150)

    # Discussable objects...
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    topic_object = GenericForeignKey()


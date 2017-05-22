from django.apps import AppConfig
from django.db.models.signals import post_init, post_save


class DiscussionConfig(AppConfig):
    name = 'openlab.discussion'
    verbose_name = 'Discussion'

    def ready(self):
        from .signals import message_save, thread_save, Message, Thread
        post_save.connect(message_save, sender=Message)
        post_save.connect(thread_save, sender=Thread)

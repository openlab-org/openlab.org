import sys
import os.path
from random import choice

# django
from django.contrib import admin
from django.core.management.base import BaseCommand, CommandError

# first party
from openlab.core import util

# local
from notifications.models import Notification
from notifications.email import send_digest

import logging
logger = logging.getLogger("openlab")
PAGE = 500

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Loop through all unsent notifications
        # TODO later make this only do 500, etc, at a time
        notifications = Notification.get_unsent()

        # Group by users
        grouped = {}
        users = {}
        for notification in notifications:
            k = int(notification.user_id)
            if k not in grouped:
                users[k] = notification.user
                grouped[k] = []
            grouped[k].append(notification)

        # Send to each user
        for user_id, notifications in grouped.iteritems():
            user = users[user_id]
            logger.info(" - %02i notifications for [%03i]  (%s <%s>)" % (
                    len(notifications), user_id, user, user.email))
            send_digest(user, notifications)





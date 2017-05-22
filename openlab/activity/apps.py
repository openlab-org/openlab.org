from django.apps import AppConfig


class ActivityConfig(AppConfig):
    name = 'openlab.activity'
    verbose_name = 'Activity'

    def ready(self):
        # TODO: clean up import
        from . import signals

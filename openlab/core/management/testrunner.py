from django.test.runner import DiscoverRunner
from django.conf import settings

class AppsTestSuiteRunner(DiscoverRunner):
    """ Override the default django 'test' command, include only
        apps that are part of this project
        (unless the apps are specified explicitly)
    """
    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        if not test_labels:
            test_labels = [app
                for app in settings.INSTALLED_APPS
                if app in settings.LOCAL_APPS ]
        return super(AppsTestSuiteRunner, self).run_tests(
              test_labels, extra_tests, **kwargs)

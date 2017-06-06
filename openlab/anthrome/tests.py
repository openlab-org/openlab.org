from unittest import skip

from django.test import SimpleTestCase, TestCase
from django.test.client import Client

from django.core.urlresolvers import reverse
from openlab.users.models import User

from openlab.hubpath.models import HubPathBase
from openlab.project.factories import ProjectTestFactory
from openlab.project.models import Project
from openlab.moderation.models import FeaturedProject

# No need to flush DB after every test this way:
HubPathBase._SKIP_HUBPATH_CHECK = True

class BasicViewsTestCase(TestCase):
    #urls = 'project.urls'
    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@test.com", "asdf")
        self.project = ProjectTestFactory(user=self.user, hubpath='testuser/testproj')
        self.project.save()
        FeaturedProject.objects.create(user=self.user, project=self.project)
        self.client.login(username="testuser", password="asdf")

    @skip
    def test_view_showcase(self):
        response = self.client.get(reverse('showcase'))
        self.assertEqual(200, response.status_code)
        self.assertIn(self.project.hubpath, response.content.decode('utf-8'))


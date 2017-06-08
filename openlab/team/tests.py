from django.test import SimpleTestCase, TestCase
from django.test.client import Client

from django.core.urlresolvers import reverse
from openlab.users.models import User

from openlab.hubpath.models import HubPathBase
from openlab.team.factories import make_random
from openlab.team.models import Team

# No need to flush DB after every test this way:
HubPathBase._SKIP_HUBPATH_CHECK = True

class BasicViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@test.com", "asdf")
        self.team = make_random(1, [self.user])[0]

    def test_view_files_tab(self):
        url = reverse('team', args=(self.team.hubpath,))
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertIn(b"projects found!", response.content)

    def test_view_members_tab(self):
        url = reverse('team_members', args=(self.team.hubpath,))
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertIn(b"testuser", response.content)

    def tearDown(self):
        self.user.delete()
        self.team.delete()


class CreationTestCase(TestCase):
    SLUG = 'test-team'
    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@test.com", "asdf")
        self.client.login(username="testuser", password="asdf")
        self.team = None

    def test_create_user_team_renders_form(self):
        url = reverse('team_create')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertIn(b"testuser", response.content)
        self.assertIn(b"Name", response.content)
        # TODO fix location
        # self.assertIn("Location", str(response.content))

    def test_create_new_team(self):
        post_data = {
            # csrfmiddlewaretoken:Zk7myJlugfXBPAm49mF4CKR9FEtZsvNG
            'title': 'Test Team',
            'slug': self.SLUG,
            'summary': 'test team summary',
            'visibility': 'pu',
            'location': '',
            'submit': 'Save',
        }
        url = reverse('team_create')
        response = self.client.post(url, post_data)
        self.assertEqual(302, response.status_code)
        self.assertIn(self.SLUG, str(response))
        self.team = Team.objects.order_by('-id')[0]
        self.assertEqual(self.team.slug, self.SLUG)

    def tearDown(self):
        self.user.delete()
        if self.team:
            self.team.delete()


class ManageViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@test.com", "asdf")
        self.team = make_random(1, [self.user])[0]
        self.client.login(username="testuser", password="asdf")

    def test_view_update_tab(self):
        url = reverse('team_manage_members', args=(self.team.hubpath,))
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertIn(b"Add user", response.content)

    def test_view_media_tab(self):
        url = reverse('team_manage_gallery', args=(self.team.hubpath,))
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertIn(b"photos yet!", response.content)

    def test_view_edit_tab(self):
        url = reverse('team_manage_edit', args=(self.team.hubpath,))
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertIn(b"Name", response.content)
        self.assertIn(self.team.title, str(response.content)) # ensure filled in
        # TODO fix location
        # self.assertIn("Location", str(response.content))

    def tearDown(self):
        self.user.delete()
        self.team.delete()

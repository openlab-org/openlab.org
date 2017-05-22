from django.test import SimpleTestCase, TestCase
from django.test.client import Client

from django.core.urlresolvers import reverse
from openlab.users.models import User

from openlab.hubpath.models import HubPathBase
from openlab.project.factories import ProjectTestFactory
from openlab.project.models import Project

# No need to flush DB after every test this way:
HubPathBase._SKIP_HUBPATH_CHECK = True

class BasicViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@test.com", "asdf")
        self.project = ProjectTestFactory(user=self.user, hubpath='testuser/testproj')
        self.project.save(skip_hubpath_check=True)

    def test_view_files_tab(self):
        url = reverse('project_files', args=(self.project.hubpath,))
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        #self.assertIn(b"project doesn't have any files", response.content)
        self.assertIn(b"First created", response.content)

    def test_view_forks_tab(self):
        url = reverse('project_forks', args=(self.project.hubpath,))
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertIn(b"has not yet been forked", response.content)

    def test_view_members_tab(self):
        url = reverse('project_members', args=(self.project.hubpath,))
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertIn(b"testuser", response.content)

    def tearDown(self):
        self.user.delete()
        self.project.delete()


class CreationTestCase(TestCase):
    #urls = 'project.urls'
    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@test.com", "asdf")
        self.client.login(username="testuser", password="asdf")
        self.project = None

    def test_create_user_project_renders_form(self):
        url = reverse('project_create', args=('testuser',))
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertIn("testuser", str(response.content))
        self.assertIn("Name", str(response.content))
        # TODO fix location
        #self.assertIn("Location", str(response.content))
        self.assertIn("License", str(response.content))
        self.assertIn("GPL", str(response.content))

    def test_create_user_project_creates_new_project(self):
        post_data = {
            # csrfmiddlewaretoken:Zk7myJlugfXBPAm49mF4CKR9FEtZsvNG
            'title': 'Test Proj',
            'slug': 'test-proj',
            'summary': 'test proj sum',
            'visibility': 'pu',
            'location': '',
            'license': 'lgpl3',
            'submit': 'Save',
        }
        url = reverse('project_create', args=('testuser',))
        response = self.client.post(url, post_data)
        self.assertEqual(302, response.status_code)
        self.assertIn("testuser/test-proj", str(response))
        self.project = Project.objects.order_by('-id')[0]
        self.assertTrue(bool(self.project))
        self.assertEqual(self.project.slug, "test-proj")

    def tearDown(self):
        self.user.delete()
        if self.project:
            self.project.delete()


class ManageViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@test.com", "asdf")
        self.project = ProjectTestFactory(user=self.user, hubpath='testuser/testproj')
        self.project.save(skip_hubpath_check=True)
        self.client.login(username="testuser", password="asdf")

    def test_view_update_tab(self):
        url = reverse('project_manage_members', args=(self.project.hubpath,))
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertIn("Add user", str(response.content))

    def test_view_media_tab(self):
        url = reverse('project_manage_gallery', args=(self.project.hubpath,))
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertIn(b"photos yet!", response.content)

    def test_view_edit_tab(self):
        url = reverse('project_manage_edit', args=(self.project.hubpath,))
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertIn("Name", str(response.content))
        # TODO fix location
        #self.assertIn("Location", str(response))
        self.assertIn("License", str(response.content))
        self.assertIn("GPL", str(response.content))
        self.assertIn(self.project.title, str(response.content)) # ensure filled in

    def tearDown(self):
        self.user.delete()
        self.project.delete()


"""
Tests basic hubpath stuff
"""

from copy import deepcopy

from django.db import models

from django.test import SimpleTestCase, TestCase
from openlab.users.models import User

from openlab.project.models import Project
from openlab.team.models import Team
from openlab.team.factories import TeamTestFactory
#from project.factories import ProjectTestFactory

from django.template.defaultfilters import slugify
from . import models as hubpath_models
HubPathBase = hubpath_models
from .models import HubPathBase

class FakeTeam(HubPathBase):
    class Meta:
        app_label = 'project'
    user = models.ForeignKey(User)

class FakeProject(HubPathBase):
    class Meta:
        app_label = 'project'
    user = models.ForeignKey(User)
    team = models.ForeignKey(FakeTeam, null=True, blank=True)

class FakeService(HubPathBase):
    class Meta:
        app_label = 'project'
    user = models.ForeignKey(User)
    team = models.ForeignKey(FakeTeam, null=True, blank=True)

class FakeDoesntExist(HubPathBase):
    class Meta:
        app_label = 'project'
    user = models.ForeignKey(User)


class BaseTest(object):
    USERNAME = 'Test'
    @staticmethod
    def monkey_patch():
        # monkey patch settings
        HubPathBase._SKIP_HUBPATH_CHECK = True
        hubpath_models.single_model_names.append(('project', 'FakeTeam'))
        hubpath_models.split_model_names.append(('project', 'FakeProject'))
        hubpath_models.split_model_names.append(('project', 'FakeService'))

    def setUp(self):
        self.monkey_patch()
        self.testuser = User.objects.create_user(self.USERNAME,
                            "testuser@testuser.com", "asdfasdf")
        self.testuser.save()

        #self.team = TeamTestFactory(user=self.testuser)
        self.obj = self.make()
        self.obj.save()
        self.obj.save_cache()

    def test_get_from_hubpath(self):
        hp = self.obj.hubpath
        obj = HubPathBase.hubpath_objects.get(hubpath=hp)
        self.assertEqual(self.obj, obj)

    def test_check_delete_cache(self):
        hp = self.obj.hubpath
        self.obj.delete_cache()
        with self.assertRaises(HubPathBase.DoesNotExist):
            obj = HubPathBase.hubpath_objects.get(hubpath=hp)
        self.obj.save_cache()
        obj = HubPathBase.hubpath_objects.get(hubpath=hp)
        self.assertEqual(obj, self.obj)

    def test_check_cache_fallthrough(self):
        hp = self.obj.hubpath
        self.obj.delete_cache(True) # Actually delete cache
        obj = HubPathBase.hubpath_objects.get(hubpath=hp)
        self.assertEqual(obj, self.obj)
        self.obj.delete_cache(False)
        with self.assertRaises(HubPathBase.DoesNotExist):
            obj = HubPathBase.hubpath_objects.get(hubpath=hp)


    def test_check_does_not_exist(self):
        with self.assertRaises(HubPathBase.DoesNotExist):
            obj = HubPathBase.hubpath_objects.get(hubpath='asdf/asdf')

        with self.assertRaises(HubPathBase.DoesNotExist):
            obj = HubPathBase.hubpath_objects.get(hubpath='asdf')

    def tearDown(self):
        self.testuser.delete()
        self.obj.delete()



class MiscTests(TestCase):
    USERNAME = 'Test'

    def test_doesnt_exist(self):
        HubPathBase._SKIP_HUBPATH_CHECK = True
        self.testuser = User.objects.create_user(self.USERNAME,
                            "test@test.com", "asdf")

        self.obj = FakeDoesntExist(user=self.testuser)
        with self.assertRaises(HubPathBase.ConfigError):
            self.obj.save()

    def test_arbitrary_get(self):
        BaseTest.monkey_patch()
        HubPathBase._SKIP_HUBPATH_CHECK = True
        self.testuser = User.objects.create_user(self.USERNAME,
                            "test@test.com", "asdf")
        obj1 = FakeTeam(user=self.testuser, slug='test-slug1')
        obj1.save()
        obj2 = FakeTeam(user=self.testuser, slug='test-slug2')
        obj2.save()

        obj3 = FakeProject(user=self.testuser, slug='test-slug3')
        obj3.save()
        obj4 = FakeProject(team=obj1, user=self.testuser, slug='test-slug4')
        obj4.save()

        # Make sure random stuff raises errors
        with self.assertRaises(HubPathBase.DoesNotExist):
            HubPathBase.hubpath_objects.arbitrary_get(asdf='asdf')

        with self.assertRaises(HubPathBase.DoesNotExist):
            HubPathBase.hubpath_objects.arbitrary_get(slug='NOPE')

        for i in range(1, 5):
            result = HubPathBase.hubpath_objects.arbitrary_get(slug='test-slug%i' % i)
            self.assertEqual(locals()['obj%i' % i], result)

        # TODO This test is broken
        #obj4_res = HubPathBase.hubpath_objects.arbitrary_get(team=obj1)
        #self.assertEquals(obj4, obj4_res)

    def test_conflicting_hubpath(self):
        # Only one not to skip hubpath test
        BaseTest.monkey_patch()
        self.testuser = User.objects.create_user(self.USERNAME,
                            "test@test.com", "asdf")
        HubPathBase._SKIP_HUBPATH_CHECK = False

        obj1 = FakeTeam(user=self.testuser, slug=self.USERNAME)
        with self.assertRaises(HubPathBase.DuplicateHubPath):
            obj1.save()

        DUPE = 'dupe-test-slug'

        # Only one not to skip hubpath test
        obj1 = FakeProject(user=self.testuser, slug=DUPE)
        obj1.save()
        hp = obj1.hubpath
        obj2 = FakeService(user=self.testuser, slug=DUPE)
        with self.assertRaises(HubPathBase.DuplicateHubPath):
            obj2.save()

        # Save again, to make sure
        first = HubPathBase.hubpath_objects.get(hubpath=hp)
        self.assertEqual(first, obj1)
        first.save(force_hubpath_check=True)


class TestTeam(BaseTest, TestCase):
    def make(self):
        return FakeTeam(user=self.testuser, slug='test-slug')

    def test_hubpath(self):
        self.assertEqual(self.obj.hubpath, self.obj.slug)


class TestProjectWithUser(BaseTest, TestCase):
    def make(self):
        return FakeProject(user=self.testuser, slug='test-project-slug')

    def test_hubpath(self):
        self.assertEqual(self.obj.hubpath,
                "/".join([self.USERNAME, self.obj.slug]))


class TestProjectWithTeam(BaseTest, TestCase):
    TEAM_SLUG = 'icky-slug'
    def make(self):
        team = FakeTeam(slug=self.TEAM_SLUG, user=self.testuser)
        team.save()
        return FakeProject(team=team, user=self.testuser, slug='test-project-slug')

    def test_hubpath(self):
        self.assertEqual(self.obj.hubpath,
                "/".join([self.TEAM_SLUG, self.obj.slug]))


"""
Tests all discussion stuff
"""
from copy import deepcopy

from django.views.generic.base import View
from django.test import SimpleTestCase, TestCase
from django.test import Client

from openlab.users.models import User
from .views import DiscussableMixin


class TestMixinView(View, DiscussableMixin):
    def get(self, request, *a, **k):
        pass

    def post(self, request, *a, **k):
        pass

class MixinTestCase(TestCase):
    def test_plain_view(self):
        pass




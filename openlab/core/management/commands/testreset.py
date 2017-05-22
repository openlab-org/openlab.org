from django.contrib import admin
from django.core.management.base import BaseCommand , CommandError
import sys
import os.path
from random import randint, choice, choice, choice, choice
from datetime import datetime
from django.conf import settings

from random_words import RandomWords

from openlab.users.models import User
from openlab.team.factories import make_random as make_random_teams
from openlab.project.factories import make_random as make_random_projects
from openlab.accounts.factories import random_user

from openlab.moderation.models import FeaturedProject

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Make some users
        users = []
        janetest = random_user("janetest", "Jane", "Test", is_super=True)
        users.append(janetest)
        users.append(random_user("joetest", "Joe", "Test", is_super=True))
        users.append(random_user("AnotherTestUser", is_super=True))
        users.append(random_user("MizzTestarific", is_super=True))

        for i in range(10):
            # Make more users
            users.append(random_user())


        # Makes a bunch of teams
        teams = make_random_teams(10, users)

        # Make a bunch of projects
        projects = make_random_projects(30, users, teams)

        # Get 6 projects to make them "featured ones"
        featured = [choice(projects) for i in range(6)]

        # First delete all current featured projects
        FeaturedProject.objects.all().delete()

        # now create a bunch of featured projects
        for proj in featured:
            FeaturedProject.objects.create(project=proj, user=janetest)



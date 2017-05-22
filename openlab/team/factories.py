import factory
from core.factories import InfoBaseTestFactory
from . import models

from random import choice, randint

class TeamTestFactory(InfoBaseTestFactory):
    FACTORY_FOR = models.Team

def make_random(count, users):
    results = []
    for i in range(count):
        owner = choice(users)
        members = []
        # Add a few users
        for i in range(randint(0, 3)):
            user = choice(users)
            if user not in members:
                members.append(user)

        team = TeamTestFactory.build(user=owner)
        team.save()
        for member in members:
            team.members.add(member)

        results.append(team)

    return results



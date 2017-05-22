import factory
from factory import fuzzy
from core.factories import InfoBaseTestFactory
from . import models

from anthrome import anthrome_types

from random import choice, randint

class ProjectTestFactory(InfoBaseTestFactory):
    FACTORY_FOR = models.Project
    #version = factory.Sequence(lambda n: "0." + ".".join(str(n)))

    @factory.lazy_attribute
    def biome(a):
        return choice( [i[0] for i in anthrome_types.CHOICES])

def make_random(count, users, teams):
    results = []
    for i in xrange(count):
        owner = choice(users)
        team_owner = choice(teams)
        if i % 3 == 0:
            # One third are team projects
            project = ProjectTestFactory(user=owner, team=team_owner)
        else:
            # The others are user specific
            project = ProjectTestFactory(user=owner)

        project.save()
        results.append(project)

    return results



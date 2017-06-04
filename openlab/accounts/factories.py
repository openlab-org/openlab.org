import factory
from . import models
from openlab.users.models import User
from django.template.defaultfilters import slugify

from random import choice, randint


from core.factories import halfrand, li, rw

from random_words import RandomNicknames
rn = RandomNicknames()


def bio():
    paras = []
    for i in range(halfrand(4)):
        para = li.get_sentences(halfrand(20))

        if randint(0, 4):
            # insert first a "title"
            paras.append('%s\n------------\n'
                        % rw.random_word().capitalize)

        paras.append(para)
    return '\n\n'.join(paras)

last_names = """Holland Shapiro Pickens Harte Bruckner Zimmer Orman York
Garber Grimes Howell Harmes O'Connolly Harris Brighton Kay O'Brian Bennington
Marx Grayson Benson LeRoy Stevens Thayer Hyde Carr Walker Hamley Thomas Zoer
Swanson Heron Daley Davis Parker Nichols Carter Hunter Matthews McGuire Clark
Chapman Kaufman Zumbelh Wright McCourt McCreary Tredway Ketchum Brockman
Crossman Gomer Green Peluso Schulze Sorter Wallace Welch Nordmann Wheeler
Whitman Wilding Barnett Schenk Kieffer Roberts Collings Kindell Himbeck
Everest Zorr Adams Bray Colton Holt Kayson McDaniel Jacobs Preston Harven
Marshall""".split()


def _nick_name(f, l):
    rand_word = lambda s: rw.random_word(str(s[0]).lower())
    return ("%s_%s" % (rand_word(f), rand_word(l))).lower()

usernamers = [
        lambda f, l: (u"%s.%s" % (f, l)).replace("'", ""),
        lambda f, l: f.lower(),
        lambda f, l: u"%s-%s" % (f, rw.random_word()),
        lambda f, l: u"%s%i" % (rw.random_word(), randint(0, 300)),
        lambda f, l: u"%s%i" % (f, randint(0, 300)),
        _nick_name, _nick_name, _nick_name,
    ]


def random_user(username=None, first_name=None, last_name=None, is_super=False):
    try:
        first_name = first_name or rn.random_nick()
    except ValueError:
        # erm version issue??
        first_name = first_name or rn.random_nick(gender=choice("mfu"))
    last_name = last_name or choice(last_names)
    username = username or choice(usernamers)(first_name, last_name)

    name = username

    if not User.objects.filter(username=name):
        joetest = User.objects.create_user(name,
                "%s@test.com"%name, "asdf")
    else:
        joetest = User.objects.get(username=name)
    joetest.is_superuser = is_super
    joetest.is_staff = is_super
    joetest.first_name = first_name
    joetest.last_name = last_name
    joetest.save()

    profile = joetest.profile
    profile.description = bio()
    profile.regenerate_markdown()

    profile.prefered_name = choice(['w', 'w', 'w', 'f', 'u'])
    return joetest



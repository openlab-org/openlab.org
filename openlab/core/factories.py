import factory
from . import models
from django.template.defaultfilters import slugify

from random import choice, randint


from random_words import RandomWords, LoremIpsum

rw = RandomWords()
li = LoremIpsum()

def fake_markdown():
    # TODO: Take over Riker Ipsum
    p = []
    for i in range(randint(1, 4)):
        p.append(rikeripsum.generate_paragraph())

    return "\n\n".join(p)

def halfrand(b, ratio=1):
    if randint(0, ratio):
        return randint(1, b// (ratio + 1))
    else:
        return randint(1, b)

def fake_projects(user):
    from project.models import Project
    rw = RandomWords()
    for i in range(10):
        title = ' '.join(rw.random_words(count=halfrand(20))).capitalize()



# Huge bias toward the first 4 items so we have "more popular" tags
POSSIBLE_TAGS = ['ecology']*5 + ['medicine']*5 + ['maker']*5 + ['green']*5 + [
    'beans', 'baseline', 'barometers', 'probabilities',
    'humidity', 'deposit', 'wraps', 'study',
    'subfunction', 'telecommunication',
    'vibration', 'merchandise', 'drawer', 'rag',
    'challenge', 'rattle', 'pull', 'harness',
    'evaporation', 'nickel', 'coordinates',
    'probability', 'ease', 'flap', 'storm']



def fake_tags(a):
    # on averge 20 random tags
    tagset = set()
    for i in range(halfrand(30)):
        tag = choice(POSSIBLE_TAGS)
        tagset.add(tag)
    return tagset

markdowns = ['*%s*', '`%s`', '_%s_']


def _random_markdown(s):
    words = s.split()
    new_para = []
    for word in words:
        if not randint(0, 7) and word.isalpha(): # 1 out of 7 words
            word = '*%s*' % word
        new_para.append(word)

    return ' '.join(new_para)


class InfoBaseTestFactory(factory.Factory):
    #title = fake_title
    #tags = fake_tags
    #summary = fake_summary
    #description = fake_description

    @factory.post_generation
    def generate_tags(self, create, *a, **k):
        if not create:
            # Simple build, do nothing.
            pass
        tags = fake_tags(self)
        #print tags
        #for tag in tags:
        #    self.tags.add(tag)

    @factory.lazy_attribute
    def title(a):
        return ' '.join(rw.random_words(count=halfrand(20, 4))).capitalize()

    @factory.lazy_attribute
    def slug(a):
        r = slugify(a.title)
        if len(r) > 31:
            r = r[:24] + ("%04i" % randint(1, 9999))
        return r

    @factory.lazy_attribute
    def summary(a):
        s = 'X' * 150
        while len(s) > 140:
            # Generate either 1 or 2 sentences, must be below 140
            s = li.get_sentences(randint(1, 2))
        return s

    #@factory.lazy_attribute
    #def description(a):
    #    paras = []
    #    for i in range(halfrand(20)):
    #        if randint(0, 3): # 3/4 time use lorem ipsum
    #            para = li.get_sentences(halfrand(20))
    #        else:
    #            para = rikeripsum.generate_paragraph()
    #        if randint(0, 4):
    #            # insert first a "title"
    #            paras.append('%s\n------------\n' % rw.random_word().capitalize())
    #        paras.append(para)
    #    return '\n\n'.join(paras)



import factory
from . import models
from django.template.defaultfilters import slugify

from random import choice, randint

from .models import WikiPage, WikiSite

from core.factories import rw, li


class InfoBaseTestFactory(factory.Factory):
    for_model = WikiPage

    @factory.lazy_attribute
    def title(a):
        return ' '.join(rw.random_words(count=halfrand(20, 4))).capitalize()

    @factory.lazy_attribute
    def text(a):
        paras = []
        for i in range(halfrand(20)):
            if randint(0, 3): # 3/4 time use lorem ipsum
                para = li.get_sentences(halfrand(20))
            else:
                para = rikeripsum.generate_paragraph()

            if randint(0, 4):
                # insert first a "title"
                paras.append('%s\n------------\n' % rw.random_word().capitalize())

            paras.append(para)
        return '\n\n'.join(paras)






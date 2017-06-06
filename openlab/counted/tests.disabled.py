"""
Tests counted stuff
"""
import threading
import random

from copy import deepcopy

from django.db import models

from django.test import SimpleTestCase, TestCase, TransactionTestCase, skipUnlessDBFeature
from openlab.users.models import User

from .models import ScopeBase, CountedBase

class FakeGallery(ScopeBase):
    class Meta:
        app_label = 'fakegallery'
    data = models.CharField(default='x', max_length=12)
    pass

class FakePhoto(CountedBase):
    def __str__(self):
        #print (self.gallery_id, self.number)
        #return ""
        return u"<PHOTO %i - %i>" % (self.gallery_id, self.number)

    class Meta:
        unique_together = (CountedBase.unique_together('gallery'), )
        index_together = (CountedBase.unique_together('gallery'), )
        app_label = 'fakegallery'

    COUNTED_SCOPE = 'gallery'
    gallery = models.ForeignKey(FakeGallery)


class PhotoCreationThread(threading.Thread):
    def __init__(self, gallery):
        threading.Thread.__init__(self)
        self.gallery = gallery

    def run(self):
        self.photo = FakePhoto(gallery=self.gallery)
        self.photo.save()


class BaseTest(TestCase):
    def setUp(self):
        self.gallery = FakeGallery()
        self.gallery.save()

    def test_create(self):
        photos = []
        for i in range(1, 6):
            photo = FakePhoto(gallery=self.gallery)
            photo.save()
            photos.append(photo)

        for i in range(1, 6):
            photo = FakePhoto.objects.get(gallery=self.gallery, number=i)
            self.assertEquals(photos[i-1], photo)


    def test_multi_random(self):
        galls = []
        for i in range(1, 5):
            g = FakeGallery()
            g.save()
            galls.append(g)

        photos = []
        for j in range(20):
            g = random.choice(galls)
            photo = FakePhoto(gallery=g)
            photo.save()
            photos.append(photo)



class Threading(TransactionTestCase):
    def setUp(self):
        self.gallery = FakeGallery()
        self.gallery.save()

    #@skipUnlessDBFeature('supports_transactions')
    def test_threading(self):
        return # SKIPPING beacuse in-memory sqlite doesnt support threads
        threads = []
        for i in range(10):
            t = PhotoCreationThread(self.gallery)
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()
            #print t.photo.id




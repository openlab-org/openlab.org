# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-08 01:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        ('gallery', '0001_initial'),
        ('cities_light', '0006_compensate_for_0003_bytestring_bug'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='photo',
            field=models.ForeignKey(blank=True, help_text='So what do you look like?', null=True, on_delete=django.db.models.deletion.CASCADE, to='gallery.Photo'),
        ),
        migrations.AddField(
            model_name='profile',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cities_light.Region'),
        ),
    ]
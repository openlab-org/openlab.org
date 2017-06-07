# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-07 23:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('project', '0001_initial'),
        ('moderation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='featuredproject',
            name='project',
            field=models.ForeignKey(help_text='Specify the project you want to feature!', on_delete=django.db.models.deletion.CASCADE, to='project.Project'),
        ),
    ]

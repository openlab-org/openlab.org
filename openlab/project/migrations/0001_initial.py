# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-08 01:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import licensefield.fields
import openlab.core.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(db_index=False, max_length=32)),
                ('hubpath', models.CharField(db_index=True, help_text="Absolute URL for this, ie 'team-name/project-name' or 'team-name'", max_length=96, unique=True)),
                ('olmarkdown_rendered', models.TextField(blank=True, help_text='HTML for rendered OL Markdown')),
                ('olmarkdown_summary', models.TextField(blank=True, help_text='Text-only suffix of rendered, for rendered OL Markdown')),
                ('olmarkdown_rendered_date', models.DateTimeField(blank=True, null=True)),
                ('street_address', models.TextField(blank=True, default='', help_text='Street address for the project.')),
                ('longitude', models.DecimalField(blank=True, decimal_places=5, help_text='Longitude for the project', max_digits=8, null=True)),
                ('latitude', models.DecimalField(blank=True, decimal_places=5, help_text='Latitude for the project', max_digits=8, null=True)),
                ('title', models.CharField(max_length=255, verbose_name='Name')),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('summary', models.CharField(help_text='Describe in in 140 characters or less. (No paragraphs.)', max_length=140, verbose_name='Summary')),
                ('visibility', models.CharField(choices=[('pu', 'Public'), ('un', 'Unlisted'), ('og', 'Need to log in'), ('pr', 'Private'), ('lp', 'Locked - Private'), ('lu', 'Locked - Unlisted'), ('lo', 'Locked - Logged in only')], db_index=True, default='pu', max_length=2)),
                ('git_url', models.URLField(blank=True, help_text='URL to Git repository', null=True)),
                ('license', licensefield.fields.LicenseField(choices=[('pd', 'Public domain'), ('cc-by', 'Creative Commons Attribution'), ('cc-by-sa', 'Creative Commons Attribution-ShareAlike'), ('gpl3', 'GPL 3.0'), ('lgpl3', 'LGPL 3.0'), ('tapr', 'TAPR Open Hardware'), ('cern', 'CERN Open Hardware')], default='pd', help_text='License for the entire project', max_length=24)),
                ('biome', models.CharField(choices=[('11', 'Urban'), ('12', 'Mixed settlements'), ('21', 'Rice villages'), ('22', 'Irrigated villages'), ('23', 'Rainfed villages'), ('24', 'Pastoral villages'), ('31', 'Residential irrigated croplands'), ('32', 'Residential rainfed croplands'), ('33', 'Populated croplands'), ('34', 'Remote croplands'), ('41', 'Residential rangelands'), ('42', 'Populated rangelands'), ('43', 'Remote rangelands'), ('51', 'Residential woodlands'), ('52', 'Populated woodlands'), ('53', 'Remote woodlands'), ('54', 'Inhabited treeless and barren lands'), ('61', 'Wild woodlands'), ('62', 'Wild treeless and barren lands')], help_text='Choose the anthrome to which this project is most related to.', max_length=2)),
            ],
            options={
                'abstract': False,
                'get_latest_by': 'updated_date',
            },
            bases=(openlab.core.models.UpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='TeamPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('view', models.BooleanField(default=True)),
                ('contribute', models.BooleanField(default=True)),
                ('change', models.BooleanField(default=True)),
                ('revert', models.BooleanField(default=True)),
                ('invite', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('view', models.BooleanField(default=True)),
                ('contribute', models.BooleanField(default=True)),
                ('change', models.BooleanField(default=True)),
                ('revert', models.BooleanField(default=True)),
                ('invite', models.BooleanField(default=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userpermission_permission', to='project.Project')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

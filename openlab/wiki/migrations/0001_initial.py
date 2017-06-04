# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-04 18:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WikiPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('olmarkdown_rendered', models.TextField(blank=True, help_text='HTML for rendered OL Markdown')),
                ('olmarkdown_summary', models.TextField(blank=True, help_text='Text-only suffix of rendered, for rendered OL Markdown')),
                ('olmarkdown_rendered_date', models.DateTimeField(blank=True, null=True)),
                ('title', models.CharField(max_length=255, verbose_name='Page title')),
                ('slug', models.SlugField()),
                ('text', models.TextField(help_text='The content of the Wikipage. <em>(Markdown syntax is available.)</em>', verbose_name='Page text')),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='WikiSite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_editable', models.BooleanField(default=True, help_text='Turn this on to enable the wiki to be editable by anyone', verbose_name='Enable public editing')),
                ('is_disabled', models.BooleanField(default=False, help_text='Temporarily disable the wiki system, for both editing and viewing (without deleting it).', verbose_name='Disable Wiki')),
                ('is_public', models.BooleanField(default=True, help_text='Disable to hide the wiki to non-contributors', verbose_name='Wiki is visible to all')),
                ('index', models.ForeignKey(blank=True, help_text='The index page for this site', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='index_page', to='wiki.WikiPage')),
            ],
        ),
        migrations.AddField(
            model_name='wikipage',
            name='site',
            field=models.ForeignKey(help_text='The site this page belongs to.', on_delete=django.db.models.deletion.CASCADE, to='wiki.WikiSite'),
        ),
        migrations.AlterUniqueTogether(
            name='wikipage',
            unique_together=set([('site', 'slug')]),
        ),
        migrations.AlterIndexTogether(
            name='wikipage',
            index_together=set([('site', 'slug')]),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-04 16:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import openlab.counted.models
import openlab.discussion.models
import openlab.prequeue.models
import s3uploader.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preview_image_thumb', models.ImageField(blank=True, help_text='Image thumb', upload_to=openlab.prequeue.models.thumb_builder)),
                ('preview_image', models.ImageField(blank=True, help_text='Full size image preview', upload_to=openlab.prequeue.models.image_builder)),
                ('preview_file', models.FileField(blank=True, help_text='File in alternative format for preview', upload_to=openlab.prequeue.models.preview_builder)),
                ('preview_html', models.TextField(blank=True, help_text='Text for a plug-in based preview of the file')),
                ('preview_tried', models.BooleanField(db_index=True, default=False, help_text='Have we yet tried encoding a preview for this file? (ie or is it still on the queue)')),
                ('preview_tried_date', models.DateField(blank=True, help_text='When did we last try encoding a preview for this file? (Useful for if we start supporting new preview formats.)', null=True)),
                ('filename', models.CharField(help_text='Original filename of file', max_length=255)),
                ('description', models.TextField(blank=True, help_text='A longer description, or notes about this file', max_length=2048)),
                ('path', models.FileField(help_text='Actual file', upload_to=openlab.discussion.models.file_path_builder)),
                ('size', models.PositiveIntegerField(help_text='Size in bytes of the file')),
                ('is_uploaded', models.BooleanField(default=False, help_text='Has the file successfully finished uploading?')),
                ('deleted', models.BooleanField(default=False, help_text='Has this entry been deleted?')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, s3uploader.models.GenericUploadableMixin),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', openlab.counted.models.AutoScopedNumberField(db_index=True, editable=False)),
                ('olmarkdown_rendered', models.TextField(blank=True, help_text='HTML for rendered OL Markdown')),
                ('olmarkdown_summary', models.TextField(blank=True, help_text='Text-only suffix of rendered, for rendered OL Markdown')),
                ('olmarkdown_rendered_date', models.DateTimeField(blank=True, null=True)),
                ('last_edited', models.DateTimeField(auto_now=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('is_edited', models.BooleanField(default=False)),
                ('is_flagged', models.BooleanField(db_index=True, default=False)),
                ('is_deleted', models.BooleanField(db_index=True, default=False)),
                ('text', models.TextField(help_text='Message text. <em>(Markdown syntax is available.)</em>', verbose_name='Text')),
            ],
            options={
                'get_latest_by': 'creation_date',
            },
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.PositiveIntegerField(default=0, editable=False, help_text='Total number of items ever added')),
                ('last_edited', models.DateTimeField(auto_now=True, db_index=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('is_private', models.BooleanField(db_index=True, default=False, help_text='If this thread is private to subscribers.')),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('title', models.CharField(help_text='Topic for the discussion thread.', max_length=255, verbose_name='Title')),
            ],
            options={
                'get_latest_by': 'last_edited',
            },
        ),
        migrations.CreateModel(
            name='ThreadSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_participant', models.BooleanField(db_index=True, default=True)),
                ('is_email_subscription', models.BooleanField(db_index=True, default=True)),
                ('last_viewed', models.DateTimeField(auto_now=True)),
                ('thread', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='discussion.Thread')),
            ],
        ),
    ]

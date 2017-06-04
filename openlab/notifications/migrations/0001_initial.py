# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-04 18:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relevance', models.PositiveSmallIntegerField(choices=[(40, 'Private'), (30, 'Direct'), (20, 'Adjacent'), (10, 'Following')], default=20)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('message', models.CharField(max_length=255)),
                ('read', models.BooleanField(db_index=True, default=False, help_text='If its been read.')),
                ('mailed', models.BooleanField(db_index=True, default=False, help_text='if an email alert was sent for this notifiaction')),
                ('url', models.CharField(blank=True, max_length=255, null=True)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
            ],
            options={
                'get_latest_by': '-creation_date',
            },
        ),
    ]

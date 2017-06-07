# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-07 23:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cities_light', '0006_compensate_for_0003_bytestring_bug'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
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
                ('description', models.TextField(blank=True, default='', help_text='Tell the community a bit about yourself!', verbose_name='About me')),
                ('prefered_name', models.CharField(choices=[('w', '...first name then last name'), ('i', '...first name then last initial'), ('f', '...first name only'), ('u', '...username only')], default='w', help_text='We know how annoying it is when people call you by thewrong name. So try to get the little things right.', max_length=1, verbose_name='Refer to me with my...')),
                ('plaintext_email', models.BooleanField(default=False, help_text='Send me only ugly emails.', verbose_name='Plain text emails')),
                ('email_notification', models.BooleanField(default=True, help_text="You can disable email notifications altogether, but we promise we won't bug you.", verbose_name='Enable email notifications')),
                ('city', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cities_light.City')),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cities_light.Country')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

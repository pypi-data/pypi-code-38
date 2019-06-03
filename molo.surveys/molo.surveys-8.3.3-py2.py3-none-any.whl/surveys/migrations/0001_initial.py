# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0023_alter_page_revision_on_delete_behaviour'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MoloSurveyFormField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort_order', models.IntegerField(null=True, editable=False, blank=True)),
                ('label', models.CharField(help_text='The label of the form field', max_length=255, verbose_name='label')),
                ('field_type', models.CharField(max_length=16, verbose_name='field type', choices=[('singleline', 'Single line text'), ('multiline', 'Multi-line text'), ('email', 'Email'), ('number', 'Number'), ('url', 'URL'), ('checkbox', 'Checkbox'), ('checkboxes', 'Checkboxes'), ('dropdown', 'Drop down'), ('radio', 'Radio buttons'), ('date', 'Date'), ('datetime', 'Date/time')])),
                ('required', models.BooleanField(default=True, verbose_name='required')),
                ('choices', models.CharField(help_text='Comma separated list of choices. Only applicable in checkboxes, radio and dropdown.', max_length=512, verbose_name='choices', blank=True)),
                ('default_value', models.CharField(help_text='Default value. Comma separated values supported for checkboxes.', max_length=255, verbose_name='default value', blank=True)),
                ('help_text', models.CharField(max_length=255, verbose_name='help text', blank=True)),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MoloSurveyPage',
            fields=[
                ('page_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('intro', models.TextField(blank=True)),
                ('thank_you_text', models.TextField(blank=True)),
                ('allow_anonymous_submissions', models.BooleanField(default=False, help_text=b'Check this to allow users who are NOT logged in to complete surveys.')),
                ('allow_multiple_submissions_per_user', models.BooleanField(default=False, help_text=b'Check this to allow logged in users to complete a survey more than once. This setting has no effect on anonymous submissions.')),
                ('show_results', models.BooleanField(default=False, help_text=b'Whether to show the survey results to the user after they have submitted their answer(s).')),
                ('multi_step', models.BooleanField(default=False, help_text=b'Whether to display the survey questions to the user one at a time, instead of all at once.', verbose_name=b'Multi-step')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.CreateModel(
            name='MoloSurveySubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('form_data', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='submit time')),
                ('page', models.ForeignKey(related_name='+', to='wagtailcore.Page')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['created_at'],
                'abstract': False,
                'verbose_name': 'form submission',
            },
        ),
        migrations.AddField(
            model_name='molosurveyformfield',
            name='page',
            field=modelcluster.fields.ParentalKey(related_name='survey_form_fields', to='surveys.MoloSurveyPage'),
        ),
    ]

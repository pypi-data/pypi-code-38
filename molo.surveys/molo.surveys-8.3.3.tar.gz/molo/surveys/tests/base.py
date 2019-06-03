from molo.surveys.models import (
    MoloSurveyFormField,
    MoloSurveyPage,
    PersonalisableSurvey,
    SurveysIndexPage,
    PersonalisableSurveyFormField
)
from .utils import skip_logic_data


def create_molo_survey_form_field(survey, sort_order, obj):
    if obj['type'] == 'radio':
        skip_logic = skip_logic_data(choices=obj['choices'])
    else:
        skip_logic = None

    return MoloSurveyFormField.objects.create(
        page=survey,
        sort_order=sort_order,
        label=obj["question"],
        field_type=obj["type"],
        required=obj["required"],
        page_break=obj["page_break"],
        admin_label=obj["question"].lower().replace(" ", "_"),
        skip_logic=skip_logic
    )


def create_molo_survey_page(
        parent, title="Test Survey", slug='test-survey',
        thank_you_text='Thank you for taking the Test Survey',
        homepage_introduction='Shorter homepage introduction',
        **kwargs):
    molo_survey_page = MoloSurveyPage(
        title=title, slug=slug,
        introduction='Introduction to Test Survey ...',
        thank_you_text=thank_you_text,
        submit_text='survey submission text',
        homepage_introduction=homepage_introduction, **kwargs
    )

    parent.add_child(instance=molo_survey_page)
    molo_survey_page.save_revision().publish()

    return molo_survey_page


def create_personalisable_survey_page(
        parent, title="Test Personalisable Survey",
        slug='test-personalisable-survey',
        thank_you_text='Thank you for taking the Personalisable Survey',
        **kwargs):
    personalisable_survey_page = PersonalisableSurvey(
        title=title, slug=slug,
        introduction='Introduction to Test Personalisable Survey ...',
        thank_you_text=thank_you_text,
        submit_text='personalisable survey submission text',
        **kwargs
    )

    parent.add_child(instance=personalisable_survey_page)
    personalisable_survey_page.save_revision().publish()

    return personalisable_survey_page


def create_survey(fields={}, **kwargs):
    survey = create_molo_survey_page(SurveysIndexPage.objects.first())

    if not fields == {}:
        num_questions = len(fields)
        for index, field in enumerate(reversed(fields)):
            sort_order = num_questions - (index + 1)
            create_molo_survey_form_field(survey, sort_order, field)
    return survey


def create_molo_dropddown_field(
        parent, survey, choices, page_break=False,
        sort_order=1, label="Is this a dropdown?", **kwargs):
    return MoloSurveyFormField.objects.create(
        page=survey,
        sort_order=sort_order,
        admin_label="is-this-a-drop-down",
        label=label,
        field_type='dropdown',
        skip_logic=skip_logic_data(choices),
        required=True,
        page_break=page_break
    )


def create_personalisable_dropddown_field(
        parent, survey, choices, page_break=False,
        sort_order=1, label="Is this a dropdown?", **kwargs):
    return PersonalisableSurveyFormField.objects.create(
        page=survey,
        sort_order=sort_order,
        admin_label="is-this-a-drop-down",
        label=label,
        field_type='dropdown',
        skip_logic=skip_logic_data(choices),
        required=True,
        page_break=page_break
    )


def create_molo_survey_formfield(
        survey, field_type, label="Your favourite animal",
        required=False, sort_order=1):
    return MoloSurveyFormField.objects.create(
        page=survey,
        sort_order=sort_order,
        label=label,
        field_type=field_type,
        required=required
    )

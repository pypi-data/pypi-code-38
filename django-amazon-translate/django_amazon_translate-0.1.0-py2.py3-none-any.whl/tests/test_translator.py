from unittest.mock import call

from django_amazon_translate.tests.testapp.models import TranslatedModel


def test_translatedmodel(mocker):
    x = mocker.patch(
        'django_amazon_translate.translator._amazonTranslate.translate_text',
        return_value={'TranslatedText': 'Nothing'}
    )

    f = TranslatedModel()
    f.title_en = "Ham"
    f.description_en = "Eggs"
    f.save()

    calls = [
                call('Ham', 'en', 'de'),
                call('Ham', 'en', 'fr'),
                call('Ham', 'en', 'it'),
                call('Ham', 'en', 'es'),
                call('Eggs', 'en', 'de'),
                call('Eggs', 'en', 'fr'),
                call('Eggs', 'en', 'it'),
                call('Eggs', 'en', 'es'),
            ]

    x.assert_has_calls(calls, any_order=True)


def test_changedmodel(mocker):
    x = mocker.patch(
        'django_amazon_translate.translator._amazonTranslate.translate_text',
        return_value={'TranslatedText': 'Nothing'}
    )

    f = TranslatedModel()
    f.title_en = "Ham"
    f.description_en = "Eggs"
    f.save()

    x.reset_mock()

    f.title_en = "Spam"
    f.save()

    # Check we haven't re-translated something we shouldn't have
    # as we didn't change the field with the word Bar in it
    assert(call('Eggs', 'en', 'de') not in x.call_args_list)

    calls = [
                call('Spam', 'en', 'de'),
                call('Spam', 'en', 'fr'),
                call('Spam', 'en', 'it'),
                call('Spam', 'en', 'es'),
            ]

    x.assert_has_calls(calls, any_order=True)


def test_override(mocker):
    x = mocker.patch(
        'django_amazon_translate.translator._amazonTranslate.translate_text',
        return_value={'TranslatedText': 'Nothing'}
    )

    f = TranslatedModel()
    f.title_en = "Ham"
    f.description_en = "Eggs"
    f.save()

    x.reset_mock()

    f.title_fr = "Spam"
    f.save()

    x.assert_not_called()

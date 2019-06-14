from django.apps import AppConfig


class AmazonTranslateConfig(AppConfig):
    """
    Amazon Translate Django Application

    Utilities for models and command line to make use of Amazon Translate
    to be able to automatically translate between English and required
    languages.
    """
    name = 'django_amazon_translate'

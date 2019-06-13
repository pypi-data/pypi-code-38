"""Configuration for i18n."""

LANGUAGE_CALLBACK = lambda: 'en'

LANGUAGE_CHAIN_CALLBACK = lambda: {'*': LANGUAGE_CALLBACK()}

LANGUAGES = ['en']

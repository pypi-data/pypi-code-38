"""
Helper i18n functions.
"""
import re

from traduki import config


def reformat_language_tuple(langval):
    """Produce standardly-formatted language specification string using given language tuple.

    :param langval: `tuple` in form ('<language>', '<language variant>'). Example: ('en', 'US')
    :return: `string` formatted in form '<language>-<language-variant>'
    """
    if langval:
        langval_base, langval_variant = langval
        if langval_variant:
            langval_base = '{0}-{1}'.format(langval_base, langval_variant)

        return langval_base
    else:
        return None


def check_language_code(code_def):
    """
    Takes a language code string and checks if it is a correct one, and retrieve variant
    details if any.

    Returns:
    None in case of failure; (language_code, [language_variant]) in case of success.
    For instance:
    * check_language_code('xxx') returns None;
    * check_language_code('it') returns ('it', None);
    * check_language_code('en-us') returns ('en','us');
    """
    match = re.match('^(?P<language>[a-z]{2})(\-(?P<variant>[a-z]{2}))?$', code_def)
    if match:
        return (match.group('language'), match.group('variant'))
    else:
        return None


def get_language():
    """Get current language."""
    if not config.LANGUAGE_CALLBACK:
        raise EnvironmentError("Language callback is not configured!")
    return config.LANGUAGE_CALLBACK()


def get_chain():
    """Get language chain."""
    if not config.LANGUAGE_CHAIN_CALLBACK:
        raise EnvironmentError("Language chain callback is not configured!")
    return config.LANGUAGE_CHAIN_CALLBACK()


def get_text_from_dict(mydict, code=None, chain=None):
    """Get the text for specified language code.

    :param mydict: Language code/value dictionary.
    :param code: Language code.
    :param chain: Language code resolution chain.

    :returns: Unicode value if found or None.
    """
    if not code:
        code = get_language()
    if chain is None:
        chain = get_chain()

    _dict = dict(mydict)
    if not _dict:
        return None

    if not code:
        # code is not provided, falling back to the language chain
        if chain and '*' in chain:
            # found 'everything' chain element
            code = chain['*']
    try:
        code_base, code_variant = check_language_code(code)
    except (TypeError, KeyError):
        raise Exception('Invalid language code.')
    else:
        code = reformat_language_tuple((code_base, code_variant))

    try:
        # trying to find translation with variant
        return _dict[code]
    except KeyError:
        pass

    if code_variant:
        # we tried to find translation with variant, but failed, so falling back to without variant
        return get_text_from_dict(mydict, code_base, chain)

    if chain and code in chain and chain[code]:
        # we are able to find the code in the chain
        chain = dict(chain)  # copy to avoid changing the provided chain
        code = chain.pop(code)
        return get_text_from_dict(mydict, code, chain)

    if chain and '*' in chain and chain['*']:
        # there's 'get everything' in the language chain, falling back to it
        chain = dict(chain)  # copy to avoid changing the provided chain
        code = chain.pop('*')
        return get_text_from_dict(mydict, code, chain)

    # nothing helped, falling back to just values of the dict provided
    return next(iter(_dict.values()), None)


def get_ordered_languages():
    """Give the currently available languages, with the current default language as first item"""
    languages = get_supported_languages()
    default_lang = get_language()
    if default_lang in languages:
        languages.pop(languages.index(default_lang))
        languages.insert(0, default_lang)
    return languages


def get_supported_languages():
    """Get currently supported languages."""
    return config.LANGUAGES

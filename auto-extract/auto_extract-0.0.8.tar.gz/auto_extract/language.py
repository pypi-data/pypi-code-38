import langdetect


def get_language(tree, domain=None, lang_default="en"):
    lang = None

    if lang is None and 'lang' in tree.attrib:
        lang = tree.attrib['lang']

    if lang is None:
        page_txt = ' '.join(tree.xpath('//p/text()')) + ' '.join(tree.xpath('//div/text()'))
        if not page_txt:
            page_txt = tree.text_content()
        try:
            lang = langdetect.detect(page_txt)
        except langdetect.lang_detect_exception.LangDetectException:
            pass

    # Note that this won't work with weird domain names. A mapping is needed
    # from domain names to languages.
    if lang is None and domain is not None:
        dom = domain.split('.')[-1]
        if dom == 'com':
            return 'en'
        elif dom == 'nl':
            return 'nl'
        elif dom == 'fr':
            return 'fr'
        elif dom == "de":
            return 'de'

    if lang is None:
        return lang_default

    return lang[:2]

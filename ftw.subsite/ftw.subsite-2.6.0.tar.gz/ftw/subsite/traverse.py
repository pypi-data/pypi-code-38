from ftw.subsite.negotiator import get_subsite_language


def set_subsite_language(event):
    """Force setting the language if traversing on a subsite.
    This automatically overrides everything defined in the language tool."""

    subsite_language = get_subsite_language(event.request)
    if subsite_language:
        event.request['LANGUAGE'] = subsite_language
    else:
        return

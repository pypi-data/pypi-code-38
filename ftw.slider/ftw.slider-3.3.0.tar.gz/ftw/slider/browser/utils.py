from plone import api


def get_pane_link(pane):
    link = pane.link
    if link:
        return '{0}{1}'.format(
            api.portal.get().absolute_url(),
            link.startswith('/') and link or '/' + link)

    elif pane.external_url:
        return pane.external_url

    else:
        return ''

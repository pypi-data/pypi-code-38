from guillotina import configure
from guillotina_linkintegrity.utils import add_links  # noqa; noqa
from guillotina_linkintegrity.utils import get_aliases  # noqa
from guillotina_linkintegrity.utils import get_inherited_aliases  # noqa
from guillotina_linkintegrity.utils import get_links  # noqa
from guillotina_linkintegrity.utils import get_links_to  # noqa
from guillotina_linkintegrity.utils import remove_aliases  # noqa
from guillotina_linkintegrity.utils import remove_links  # noqa
from guillotina_linkintegrity.utils import translate_links  # noqa
from guillotina_linkintegrity.utils import update_links_from_html  # noqa


from guillotina_linkintegrity.utils import add_aliases  # noqa; noqa


app_settings = {
    'applications': [
        'guillotina.contrib.redis',
        'guillotina.contrib.cache',
        'guillotina.contrib.pubsub',
    ],
    'cache': {
        'updates_channel': 'guillotina',
        'driver': 'guillotina.contrib.redis'
    }
}


def includeme(root):
    """
    custom application initialization here
    """
    configure.scan('guillotina_linkintegrity.api')
    configure.scan('guillotina_linkintegrity.storage')
    configure.scan('guillotina_linkintegrity.subscribers')

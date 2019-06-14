import logging

# TODO mast be yml config
from tests.config import PROJECT_HOST, PROJECT_PORT, WIKI_HOST


log = logging.getLogger(__name__)


def collect_url(path, sub_domain=''):
    """
    Collects url
    :param str path:
    :param str sub_domain:
    :return str url
    """
    return 'https://{sub_domain}{domain}{port}/{path}'.format(
        path=path,
        domain=PROJECT_HOST,
        port=PROJECT_PORT,
        sub_domain=sub_domain
    )


def case_url(id):
    """
    Returns check-list page by id
    :param int id: Page id
    :return str url
    """
    return 'https://{wiki_host}{id}'.format(
        wiki_host=WIKI_HOST,
        id=id
    )

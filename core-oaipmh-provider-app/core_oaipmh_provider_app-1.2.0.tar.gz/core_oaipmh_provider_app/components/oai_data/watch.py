"""
Handle signals.
"""
from signals_utils.signals.mongo import connector, signals
from core_main_app.components.data.models import Data
from core_oaipmh_provider_app.components.oai_data import api as oai_data_api
from datetime import datetime
from core_oaipmh_provider_app.commons import status


def init():
    """ Connect to Data object events.
    """
    connector.connect(post_save_data, signals.post_save, Data)
    connector.connect(post_delete_data, signals.post_delete, Data)


def post_save_data(sender, document, **kwargs):
    """ Method executed after a saving of a Data object.
    Args:
        sender: Class.
        document: OaiData document.
        **kwargs: Args.

    """
    oai_data_api.upsert_from_data(document, force_update=True)


def post_delete_data(sender, document, **kwargs):
    """ Method executed after a deletion of a Data object.
    Args:
        sender: Class.
        document: OaiData document.
        **kwargs: Args.

    """
    try:
        oai_data = oai_data_api.get_by_data(document)
        oai_data.oai_date_stamp = datetime.now()
        oai_data.status = status.DELETED

        oai_data_api.upsert(oai_data)
    except Exception as e:
        pass

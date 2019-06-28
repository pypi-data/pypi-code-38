# -*- coding: utf-8 -*-
"""
    Initialization function
"""
from endi_base.models.base import DBSESSION
from endi_base.models.base import DBBASE


def initialize_sql(engine):
    """
        Initialize the database engine
    """
    DBSESSION.configure(bind=engine)
    DBBASE.metadata.bind = engine
    import logging
    logger = logging.getLogger(__name__)
    logger.debug("Setting the metadatas")
    DBBASE.metadata.create_all(engine)
    from transaction import commit
    commit()
    return DBSESSION

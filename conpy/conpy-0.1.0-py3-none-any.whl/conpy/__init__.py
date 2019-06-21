from .interface import (
    local_submit, mp_submit, condor_submit, condor_submit_yield, condor_resume
)

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    del handler
    del formatter
del logger

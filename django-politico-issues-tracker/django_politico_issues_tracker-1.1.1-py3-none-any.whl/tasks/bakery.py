import logging
import requests
from issuestracker.conf import settings
from celery import shared_task

logger = logging.getLogger("tasks")

BAKERY_STEPS = [
    "bake_home",
    "bake_categories",
    "bake_issues",
    "bake_candidates",
]


@shared_task(acks_late=True)
def bake():
    logger.info("Sending POST to Bakery: {}".format(settings.BAKERY_URL))
    if settings.BAKERY_URL is not None:
        for step in BAKERY_STEPS:
            logger.info("- {}".format(step))
            requests.post(
                settings.BAKERY_URL,
                data={"action": step},
                headers={
                    "Authorization": "Token: {}".format(settings.SECRET_KEY)
                },
            )
    else:
        logger.info("No bakery configured.")

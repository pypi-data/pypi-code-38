
from rook.logger import logger
from rook.processor.error import Error

from .aug_factory import AugFactory


class AugsManager(object):

    def __init__(self, trigger_services, output):
        self._trigger_services = trigger_services
        self._output = output
        self._aug_factory = AugFactory(output)
        self._augs = set()

    def add_aug(self, configuration):
        try:
            aug = self._aug_factory.get_aug(configuration)
        except Exception as exc:
            message = "Failed to parse aug"
            logger.exception(message)

            try:
                aug_id = configuration['id']
            except Exception:
                return

            self._output.send_rule_status(aug_id, "Error", Error(exc=exc, message=message))
            return

        logger.debug("Adding aug-\t%s", aug.aug_id)

        aug.add_aug(self._trigger_services)
        self._augs.add(aug.aug_id)

    def remove_aug(self, aug_id):
        logger.debug("Removing aug-\t%s", aug_id)

        self._trigger_services.remove_aug(aug_id)
        self._augs.remove(aug_id)

    def clear_augs(self):
        logger.debug("Clearing all augs")

        # Explicitly delete (and report) all augs we know about)
        for aug in self._augs.copy():
            self.remove_aug(aug)

        # Just in case- delete anything that may have been left behind
        self._trigger_services.clear_augs()

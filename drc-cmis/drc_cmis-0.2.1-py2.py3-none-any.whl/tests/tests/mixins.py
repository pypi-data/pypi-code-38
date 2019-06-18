from datetime import date

from cmislib.exceptions import ObjectNotFoundException

from drc_cmis import settings
from drc_cmis.client import cmis_client


class DMSMixin:
    def setUp(self):
        super().setUp()
        today = date.today()
        self.addCleanup(lambda: self._removeTree(f"/{settings.BASE_FOLDER_LOCATION}"))
        cmis_client._base_folder = None

    def _removeTree(self, path):
        try:
            root_folder = cmis_client._repo.getObjectByPath(path)
        except ObjectNotFoundException:
            return
        root_folder.deleteTree()

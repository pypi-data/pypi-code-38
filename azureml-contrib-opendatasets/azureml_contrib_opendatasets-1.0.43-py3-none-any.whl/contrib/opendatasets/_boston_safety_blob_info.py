# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Blob info of Boston Safety Data."""

from .dataaccess.base_blob_info import BaseBlobInfo


class BostonSafetyBlobInfo(BaseBlobInfo):
    """Blob info of Boston Safety Data."""

    def __init__(self):
        """Initialize Blob Info."""
        self.registry_id = 'city_safety_boston'
        self.blob_account_name = 'azureopendatastorage'
        self.blob_container_name = "citydatacontainer"
        self.blob_relative_path = "Safety/Release/city=Boston"
        self.blob_sas_token = (
            r"?st=2019-02-26T02%3A34%3A32Z&se=2119-02-27T02%3A34%3A00Z&sp=rl&sv=2018-03-28&sr=c"
            # [SuppressMessage("Microsoft.Security", "CS002:SecretInNextLine", Justification="Offline sas token")]
            r"&sig=XlJVWA7fMXCSxCKqJm8psMOh0W4h7cSYO28coRqF2fs%3D")

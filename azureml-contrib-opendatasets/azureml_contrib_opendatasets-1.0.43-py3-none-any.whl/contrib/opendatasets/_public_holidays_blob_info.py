# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Blob info of Public holiday Data."""

from .dataaccess.base_blob_info import BaseBlobInfo


class PublicHolidaysBlobInfo(BaseBlobInfo):
    """Blob info of Public Holiday Data."""

    def __init__(self):
        """Initialize Blob Info."""
        self.registry_id = 'public_holiday'
        self.blob_account_name = 'azureopendatastorage'
        self.blob_container_name = "holidaydatacontainer"
        self.blob_relative_path = "Processed"
        self.blob_sas_token = (
            r"?st=2019-03-11T10%3A23%3A01Z&se=9999-03-12T10%3A23%3A00Z&sp=rl&sv=2018-03-28&sr=c"
            # [SuppressMessage("Microsoft.Security", "CS002:SecretInNextLine", Justification="Offline sas token")]
            r"&sig=FZve74IozzrmHL2cBPB5c%2BsDWt0fyYR3z82xXdMczVw%3D")

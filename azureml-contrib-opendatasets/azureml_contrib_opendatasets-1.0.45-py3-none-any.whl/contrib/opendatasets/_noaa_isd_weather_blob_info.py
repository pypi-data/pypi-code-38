# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Blob info of NOAA ISD Weather Data."""

from .dataaccess.base_blob_info import BaseBlobInfo


class NoaaIsdWeatherBlobInfo(BaseBlobInfo):
    """Blob info of NOAA ISD Weather Data."""

    def __init__(self):
        """Initialize Blob Info."""
        self.registry_id = 'isd'
        self.blob_account_name = 'azureopendatastorage'
        self.blob_container_name = "isdweatherdatacontainer"
        self.blob_relative_path = "ISDWeather/"
        self.blob_sas_token = (
            r"?st=2019-01-18T03%3A10%3A05Z&se=9999-01-19T03%3A10%3A00Z&sp=rl&sv=2018-03-28&sr=c"
            # [SuppressMessage("Microsoft.Security", "CS002:SecretInNextLine", Justification="Offline sas token")]
            r"&sig=yr%2BymNXXb2Fxt8rJSi2GEgeEEtXW1%2FNk2NofF6ct9L8%3D")

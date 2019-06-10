# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Define blob info class of NOAA GFS Weather Data."""

from .dataaccess.base_blob_info import BaseBlobInfo


class NoaaGfsWeatherBlobInfo(BaseBlobInfo):
    """Blob info of NOAA GFS Weather Data."""

    def __init__(self):
        """Initialize Blob Info."""
        self.registry_id = 'gfs'
        self.blob_account_name = 'azureopendatastorage'
        self.blob_container_name = "gfsweatherdatacontainer"
        self.blob_relative_path = "GFSWeather/GFSProcessed"
        self.blob_sas_token = (
            r"?st=2019-01-18T03%3A02%3A54Z&se=9999-01-19T03%3A02%3A00Z&sp=rl&sv=2018-03-28&sr=c"
            # [SuppressMessage("Microsoft.Security", "CS002:SecretInNextLine", Justification="Offline sas token")]
            r"&sig=NI%2BpfwiCXU2ht0qUPgPdp1Q4Fxg8LDY9RokL3xtaGBw%3D")

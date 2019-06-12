"""
ObsPlus instructions for downloading dataset.
"""
from pathlib import Path

from obsplus import DataSet

from opsdata_coal_node.version import __version__


class CoalNode(DataSet):
    """
    A dataset collected over an operating longwall coalmine using a dense
    network of geophones.
    """

    name = "coal_node"
    base_path = Path(__file__).parent
    version = __version__

    # --- functions used to specify how data are downloaded

    def download_events(self):
        """ download event data and store them in self.event_path """
        Path(self.event_path).mkdir(exist_ok=True, parents=True)

    def download_waveforms(self):
        """ download waveform data and store them in self.waveform_path """
        Path(self.waveform_path).mkdir(exist_ok=True, parents=True)

    def download_stations(self):
        """ download station data and store them in self.station_path """
        Path(self.station_path).mkdir(exist_ok=True, parents=True)

    # --- properties to specify when data need to be downloaded

    # @property
    # def waveforms_need_downloading(self):
    #     """ Return True if the waveforms should be downloaded """
    #
    # @property
    # def stations_need_downloading(self):
    #     """ Return True if the stations should be downloaded """
    #
    # @property
    # def events_need_downloading(self):
    #     """ Return True if the events should be downloaded """

    # --- functions to return clients

    # @property
    # @lru_cache()
    # def waveform_client(self) -> Optional[WaveBank]:
    #     """ A cached property for a waveform client """
    #
    # @property
    # @lru_cache()
    # def event_client(self) -> Optional[EventBank]:
    #     """ A cached property for an event client """
    #
    # @property
    # @lru_cache()
    # def station_client(self) -> Optional[obspy.Inventory]:
    #     """ A cached property for a station client """

    # --- post download hook

    # def pre_download_hook(self):
    #     """ This code gets run before downloading any data. """
    #
    # def post_download(self):
    #     """ This code get run after downloading all data types. """

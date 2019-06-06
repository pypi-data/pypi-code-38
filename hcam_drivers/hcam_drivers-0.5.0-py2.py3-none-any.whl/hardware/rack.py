# module to talk to the arduino in the thermal enclosure
from hcam_widgets.gtc.corba import get_telescope_server


class GTCRackSensor(object):

    @property
    def temperature(self):
        s = get_telescope_server()
        return s.getCabinetTemperature1()

    @property
    def humidity(self):
        s = get_telescope_server()
        return s.getHumidity()

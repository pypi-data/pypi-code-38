class Rack_sensor:
    def __init__( self, *sensors ):
        self.sensors = list( sensors )

    def append( self, *sensors ):
        sensors = list( sensors )
        self.sensors += sensors

    def read( self ):
        result = {}
        for sensor in self.sensors:
            result.update( sensor.read() )
        return result

from peek_core_device._private.PluginNames import deviceTuplePrefix
from vortex.Tuple import addTupleType, TupleField, Tuple


@addTupleType
class WebClientVortexDetailsTuple(Tuple):
    """ Web Client Vortex Details Tuple

    This tuple is sent as the first tuple on every http vortex connection from the client.

    It provides the client with the websocket vortex details
    """
    __tupleType__ = deviceTuplePrefix + "WebClientVortexDetailsTuple"

    useSsl: bool = TupleField()
    httpPort: int = TupleField()
    websocketPort: int = TupleField()
    host: str = TupleField()

class _RabbitConfig:
    """Parameters for connecting to the RabbitMQ server.

    Properties:
    * host [str] - The RabbitMQ server's host name (e.g. "localhost")"""

    def __init__(self, host=None):
        self.host = host

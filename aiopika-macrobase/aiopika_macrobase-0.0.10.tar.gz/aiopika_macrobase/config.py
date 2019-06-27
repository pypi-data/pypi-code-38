from macrobase_driver.config import DriverConfig


class AiopikaDriverConfig(DriverConfig):

    LOGO: str = """
 _____       _
|  __ \     (_)               
| |  | |_ __ ___   _____ _ __ 
| |  | | '__| \ \ / / _ \ '__|
| |__| | |  | |\ V /  __/ |   
|_____/|_|  |_| \_/ \___|_|aiopika
"""

    # AMQP Broker
    RABBITMQ_USER: str = 'rabbitmq'
    RABBITMQ_PASS: str = 'test'
    RABBITMQ_HOST: str = 'localhost'
    RABBITMQ_PORT: int = 5672
    RABBITMQ_VHOST: str = '/'

    # Queue
    QUEUE_NAME: str = 'queue'
    QUEUE_AUTO_DELETE: bool = False
    QUEUE_DURABLE: bool     = True

    # Processing
    IGNORE_PROCESSED: bool = True
    REQUEUE_DELAY: int = 10
    DEFAULT_RETRY_DELAY: int = 60
    REQUEUE_IF_FAILED: bool = True  # TODO: Set `requeue` for all AiopikaException subclasses

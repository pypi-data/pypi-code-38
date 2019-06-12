from macrobase_driver.config import DriverConfig, LogFormat, LogLevel


class CeleryDriverConfig(DriverConfig):

    LOGO: str = """
 _____       _
|  __ \     (_)               
| |  | |_ __ ___   _____ _ __ 
| |  | | '__| \ \ / / _ \ '__|
| |__| | |  | |\ V /  __/ |   
|_____/|_|  |_| \_/ \___|_|celery
"""

    LOG_FORMAT = LogFormat.plain
    LOG_LEVEL = LogLevel.warning

    BLUEPRINT = 'CeleryDriver'
    RESULT_BACKEND = None
    # CELERY_IMPORTS = ('tasks',)
    # CELERY_IGNORE_RESULT = False

    BEAT_BLUEPRINT = 'CeleryDriverBeat'

    HEALTH_ENDPOINT: bool = True

    BROKER_HOST = "0.0.0.0"
    BROKER_PORT = 5672
    BROKER_URL = 'amqp://'
    BROKER_PASSWORD = ''
    BROKER_USER = 'guest'
    BROKER_VHOST = '/'

    @property
    def BROKER_URI(self):
        return f'{self.BROKER_URL}{self.BROKER_USER}:{self.BROKER_PASSWORD}@{self.BROKER_HOST}:{self.BROKER_PORT}/{self.BROKER_VHOST}'

    def get_worker_config(self) -> dict:
        return {
            'broker_host': self.BROKER_HOST,
            'broker_port': self.BROKER_PORT,
            'broker_user': self.BROKER_USER,
            'broker_password': self.BROKER_PASSWORD,
            'broker_vhost': self.BROKER_VHOST,

            'result_backend': self.RESULT_BACKEND,
        }

    def get_beat_config(self) -> dict:
        return {
            'broker_host': self.BROKER_HOST,
            'broker_port': self.BROKER_PORT,
            'broker_user': self.BROKER_USER,
            'broker_password': self.BROKER_PASSWORD,
            'broker_vhost': self.BROKER_VHOST,
        }

import json
import logging
import os
import time

from colorlog import ColoredFormatter, StreamHandler

from news2play.common import file_meta_data, file_log, folder_data_ymd
from news2play.common.configuration import storage_conf, storage_data, storage_log, audio_type
from news2play.common.cursor_utils import Spinner
from news2play.common.utils import Program, logged
from news2play.tts import TextToSpeech
from news2play.web_downloader import fid_spider

logger = logging.getLogger(__name__)


@logged(level=logging.INFO, message='text to speech...')
def text2speech():
    """
    If you prefer, you can hardcode your subscription key as a string and remove
    the provided conditional statement. However, we do recommend using environment
    variables to secure your subscription keys. The environment variable is
    set to SPEECH_SERVICE_KEY in our sample.
    For example:
    subscription_key = "Your-Key-Goes-Here"

    Endpoint: https://westus.api.cognitive.microsoft.com/sts/v1.0
    Key 1: cb42e8ea292e494c846e6d5b58289a06
    Key 2: 74fc753639094567a7733791ec9d8b02
    Key 3: 16a9c49e080d4bbbb168b572fc1579f3
    export SPEECH_SERVICE_KEY='cb42e8ea292e494c846e6d5b58289a06'
    :return:
    """
    subscription_key = '16a9c49e080d4bbbb168b572fc1579f3'

    if not subscription_key:
        if 'SPEECH_SERVICE_KEY' in os.environ:
            subscription_key = os.environ['SPEECH_SERVICE_KEY']
        else:
            print('Environment variable for your subscription key is not set.')
            exit()

    tts = TextToSpeech(subscription_key)

    # todo: token will expire in 10 mins, if the tts process it too slow, the token will expire and azure will return 401
    token_start = time.time()
    tts.get_token()

    with open(file_meta_data) as f:
        meta_data_list = json.loads(f.read())

    if Program.debugging():
        meta_data_list = meta_data_list[:3]

    for i, meta_data in enumerate(meta_data_list):
        title = meta_data['title']
        content = meta_data['news']
        author = meta_data['author']
        timestamp = meta_data['timestamp']
        filename = meta_data['filename']

        logger.info(f"top news: {i}")
        logger.info(f"title: {title}")
        logger.info(f"author: {author}")
        logger.info(f"timestamp: {timestamp}")

        f_name = os.path.join(folder_data_ymd, filename)

        token_duration = time.time() - token_start
        if token_duration / 60 > 10:
            token_start = time.time()
            tts.get_token()

        tts.save_audio(f_name, content, audio_type)


@logged(level=logging.INFO, message='download news...')
def download_news():
    news_json = fid_spider.load_news(storage_data)

    f_name = os.path.join(file_meta_data)
    with open(f_name, 'w', encoding='utf-8') as f:
        f.write(json.dumps(news_json, indent=4))


@logged(level=logging.INFO, message='storage init...')
def storage_init():
    for item in [storage_conf, storage_data, storage_log]:
        if not os.path.exists(item):
            os.makedirs(item)


@logged(level=logging.INFO, message='logging init...')
def logging_init():
    file_handler = logging.FileHandler(file_log, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    file_handler.setFormatter(file_formatter)

    # console_handler = logging.StreamHandler()
    # console_handler.setLevel(logging.INFO)
    # console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    # console_handler.setFormatter(console_formatter)

    console_handler = StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_color_formatter = ColoredFormatter(
        "%(asctime)s - %(log_color)s%(levelname)-8s%(reset)s %(message_log_color)s%(message)s",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={
            'message': {
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        },
        style='%'
    )
    console_handler.setFormatter(console_color_formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    disable_loggers = ['urllib3', 'pydub']
    for item in disable_loggers:
        logging.getLogger(item).setLevel(logging.WARNING)


def init():
    storage_init()
    logging_init()


def main():
    # todo: for debug, in current thread
    if Program.debugging():
        download_news()
        text2speech()
    else:
        with Spinner():
            download_news()
            text2speech()


def run():
    init()
    logger.info('︿(￣︶￣)︿ news to audios start...')
    main()
    logger.info('ヾ(￣▽￣)Bye~Bye~ news to audios finished.')

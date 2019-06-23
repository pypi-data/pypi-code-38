from logging.handlers import RotatingFileHandler
import os
import urllib
import urllib.request
import logging

logFile = 'crawler.log'
my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5 * 1024 * 1024,
                                 backupCount=2, encoding=None, delay=0)

formatter = logging.Formatter('%(name)s: %(asctime)s [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s')
my_handler.setFormatter(formatter)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d]'
                           ' [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='judge.log',
                    filemode='w',
                    )

logging.getLogger('').addHandler(my_handler)


DEBUG = True

if DEBUG:
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use

    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    # Now, we can log to the root logger, or any other logger. First the root...


logger = logging

# 超时秒数
HTTP_METHOD_TIMEOUT = os.getenv('HTTP_METHOD_TIMEOUT', 10)

# 获取结果次数
RESULT_COUNT = os.getenv('RESULT_COUNT', 20)

# 每两次获取结果之间间隔 / s
RESULT_INTERVAL = os.getenv('RESULT_INTERVAL', 1)

# 静态目录
STATIC_OJ_ROOT = os.getenv('STATIC_OJ_ROOT', '/home/')

# 静态url
STATIC_OJ_URL = os.getenv('STATIC_OJ_URL', 'localhost:8000/statics/')


def save_image(image_url, oj_name):
    # 保存静态文件，并返回新的url

    file_name = image_url.split('/')[-1]

    image_folder = os.path.join(STATIC_OJ_ROOT, oj_name)
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)
    path = os.path.join(image_folder, file_name)
    if os.path.exists(path):
        return STATIC_OJ_URL + oj_name + '/' + file_name

    req = urllib.request.Request(image_url)
    resp = urllib.request.urlopen(req)
    data = resp.read()
    with open(path, 'wb') as fp:
        fp.write(data)
    return STATIC_OJ_URL + oj_name + '/' + file_name

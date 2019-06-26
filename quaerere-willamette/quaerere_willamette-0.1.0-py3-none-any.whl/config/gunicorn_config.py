"""

http://docs.gunicorn.org/en/latest/settings.html
"""

import os

_HOST = os.getenv('GUNICORN_HOST', '127.0.0.1')
_PORT = os.getenv('GUNICORN_PORT', '5000')

bind = [f'{_HOST}:{_PORT}']
workers = int(os.getenv('GUNICORN_WORKERS', 4))
threads = workers
loglevel = os.getenv('GUNICORN_LOGLEVEL', 'info')
worker_class = 'eventlet'
worker_tmp_dir="/dev/shm"

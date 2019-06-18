import os
import time

VALID_EXAMPLES = ['titanic']


def download_example(name):
    if os.path.exists(name):
        raise OSError(f'Path ./{name} already exists.')
    download_name = ".kts_examples_" + str(int(time.time()))
    os.system(f"git clone https://github.com/konodyuk/kts-examples {download_name} &&"
              f" mv {download_name}/titanic . && rm -rf {download_name} && cd titanic && ./init.sh")
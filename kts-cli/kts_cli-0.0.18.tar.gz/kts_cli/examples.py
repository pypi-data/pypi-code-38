import os
import time
import shutil

VALID_EXAMPLES = ['titanic']


def download_example(args):
    name = args.name
    if os.path.exists(name):
        raise OSError(f'Path ./{name} already exists.')
    download_name = ".kts_examples_" + str(int(time.time()))
    os.system(f"git clone https://github.com/konodyuk/kts-examples {download_name}")
    shutil.move(f"{download_name}/{name}", f"{name}")
    os.system(f"""cd {name} && echo "n\ny\ny" | kts init""")
    shutil.rmtree(f"{download_name}")

import os 

SHARED_PATH = f"{os.path.dirname(os.path.abspath(__file__))}/share"
ENV_FILE_PATH = f'{SHARED_PATH}/worker.env'
IMAGE = "comcomai/exec:1.0.0"

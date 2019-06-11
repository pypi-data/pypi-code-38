from datetime import datetime
import os

def build_file_name(cwd, header_data):
    filename = os.path.join(cwd, 'outputs', 'ORI' + datetime.utcnow().strftime("%Y%m%d%H%M%S%f")[:-3] + '.txt')

    return filename
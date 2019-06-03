#   @author: 马朝威 1570858572@qq.com
#   @time: 2019-06-03 16:59

import re
import os
import json
import random
from ..unitl.getMd5 import get_md5_value
import time


def write_json(data,diretory_path, file_name=None):
    if not os.path.exists(diretory_path):
        print(''.join([diretory_path, 'not exits .']))
        os.mkdir(diretory_path)
        print(''.join([diretory_path, 'has been created !']))

    if not file_name:
        rstr = r"[\/\\\:\*\?\"\<\>\|]"
        file_name = re.sub(rstr, "_", file_name)
    else:
         file_name_string = ''.join([time.strftime('%X'), str(random.random())])
         file_name = get_md5_value(file_name_string)
    file_path = ''.join([diretory_path, file_name, '.json'])
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json_file.write(json.dumps(data, indent=4, ensure_ascii=False))


def main():
    pass


if __name__ == "__main__":
    main()










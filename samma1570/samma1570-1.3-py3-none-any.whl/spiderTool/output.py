#   @author: 马朝威 1570858572@qq.com
#   @time: 2019-05-29 0:32

import re
import os
import json


def write_into_json(diretory_path, file_name, data):
    if not os.path.exists(diretory_path):
        print(''.join([diretory_path, 'not exits .']))
        os.mkdir(diretory_path)
        print(''.join([diretory_path, 'has been created !']))
    rstr = r"[\/\\\:\*\?\"\<\>\|]"
    file_name = re.sub(rstr, "_", file_name)
    file_path = ''.join([diretory_path, file_name, '.json'])
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json_file.write(json.dumps(data, indent=4, ensure_ascii=False))









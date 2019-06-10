# -*- coding: utf-8 -*-

import json

def check_JSON(data):
    """
    檢查 JSON 資料格式  
    return:
    - 1: JSON object
    - 2: JSON string
    - -1: 格式錯誤
    """
    if isinstance(data, list):
        count = 0
        for record in data:
            if isinstance(record, dict):
                count += 1
        if count != len(data):
            return -1
        else:
            return 1
    elif isinstance(data, dict):
        return 1        
    elif isinstance(data, str):
        # check if data is a json string
        try:
            line = json.loads(data)
            return 2
        except ValueError:
            return -1
    else:
        return -1

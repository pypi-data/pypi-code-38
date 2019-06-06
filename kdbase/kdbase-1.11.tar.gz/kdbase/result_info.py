# -*- coding: utf-8 -*-

import json
from log import *
import StringIO
import gzip

def SUCCESS(result):
    ret = {}
    ret['code'] = 0
    ret['message'] = 'success'
    ret['result'] = result
    return json.dumps(ret)

def SUCCESS_GZIP(result):
    return gzip_compress(SUCCESS(result))

def gzip_compress(buf):
    out = StringIO.StringIO()
    with gzip.GzipFile(fileobj=out, mode="w") as f:
        f.write(buf)
    return out.getvalue()

def FAIL(code, msg):
    logger().error(msg)
    ret = {}
    ret['code'] = code
    ret['message'] = msg
    return json.dumps(ret)

if __name__ == '__main__':
    FAIL(1001, 'hadoop资源不足! 超出组网最大任务')


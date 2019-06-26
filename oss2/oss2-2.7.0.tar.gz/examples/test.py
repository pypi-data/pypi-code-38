# -*- coding: utf-8 -*-
import os
import oss2
import logging
from oss2.compat import to_unicode
from oss2.models import BucketLogging
import random
import string

oss2.set_stream_logger('oss2', logging.DEBUG)

access_key_id = os.getenv('OSS_TEST_ACCESS_KEY_ID', 'LTAIjF3h022K8rqV')
access_key_secret = os.getenv('OSS_TEST_ACCESS_KEY_SECRET', 'B4QReHEacb02qIOj3fKmaPTksz3Eg0')
bucket_name = os.getenv('OSS_TEST_BUCKET', 'hello-hangzws-1')
endpoint = os.getenv('OSS_TEST_ENDPOINT', 'http://oss-cn-shenzhen.aliyuncs.com')

# 创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)

def random_string(n):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(n))

# 开启日志记录。把日志保存在当前存储空间，设置日志文件存放的目录为 `logging/`。
# bucket.put_bucket_logging(BucketLogging(bucket.bucket_name, 'logging/'))
content = oss2.to_bytes(random_string(7 * 1024 * 1024))
bucket.append_object('my-object', 1, content)
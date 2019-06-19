
#消息中间件的配置信息
# BROKER_URL = [
#     'pyamqp://guest:guest@10.0.86.24:5672//',
#     'pyamqp://guest:guest@10.0.86.92:5672//',
#     'pyamqp://guest:guest@10.0.86.121:5672//'
# ]

BROKER_URL = 'pyamqp://guest:guest@10.0.85.230:5672//'

REDIS_HOST = "10.0.85.231"

#暂存任务的执行结果
RESULT_URL = "redis://%s:6379/1"%REDIS_HOST

#存储管理单个任务对应的celery任务标识
TOKENS_URL = "redis://%s:6379/2"%REDIS_HOST

#存储管理MAP/Reduce任务对应的celery任务标识
MAPREDUCE_URL = "redis://%s:6379/3"%REDIS_HOST

#负责记录批量任务的标识
BATCH_URL = "redis://%s:6379/4"%REDIS_HOST

#任务失败之后的重试等待事件
DEFAULT_RETRY_DELAY = 0

#每个失败的任务最多重试次数
DEFAULT_RETRY_TIMES = 3


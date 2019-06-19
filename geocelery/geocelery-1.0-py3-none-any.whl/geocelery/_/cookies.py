'''
用于记录用户提交的任务中包含的所有map子任务(celery标识)/reduce子任务(celery标识)
可以将celery上所有的属于同一个任务的map、reduce子任务当作一个整体进行管理
'''
import redis
from geocelery._.settings import MAPREDUCE_URL


class MapReduceCookie:
    
    MAP_TASK_PREFIX = "MAP:"            #记录最近一个启动的map任务的celeryID
    REDUCE_TASK_PREFIX = "REDUCE:"      #记录reduce任务的celeryID
    ALL_MAP_TASKS_PREFIX = "ALLMAP:"    #记录所有map子任务的celeryID
    
    @classmethod
    def exists(cls, taskid):
        '''
        判断当前任务(taskid)是否已经开始执行
        '''
        rdb = redis.StrictRedis.from_url(MAPREDUCE_URL)
        mp_exists = rdb.exists(cls.MAP_TASK_PREFIX + taskid)
        rd_exists = rdb.exists(cls.REDUCE_TASK_PREFIX + taskid)
        mr_exists = rdb.exists(cls.ALL_MAP_TASKS_PREFIX + taskid)
        return mp_exists or rd_exists or mr_exists

    @classmethod
    def setMapCeleryid(cls, taskid, mapid):
        '''
        记录最近一个启动的map任务(每个map任务在启动时都会调用这个函数)
        '''
        rdb = redis.StrictRedis.from_url(MAPREDUCE_URL)
        rdb.set(cls.MAP_TASK_PREFIX + taskid, mapid)

    @classmethod
    def getMapCeleryid(cls, taskid):
        '''
        获取最新的map任务的标识
        '''
        rdb = redis.StrictRedis.from_url(MAPREDUCE_URL)
        return rdb.get(cls.MAP_TASK_PREFIX + taskid)

    @classmethod
    def setReduceCeleryid(cls, taskid, celeryid):
        '''
        记录reduce任务的标识
        '''
        rdb = redis.StrictRedis.from_url(MAPREDUCE_URL)
        rdb.set(cls.REDUCE_TASK_PREFIX + taskid, celeryid)

    @classmethod
    def getReduceCeleryid(cls, taskid):
        '''
        返回reduce任务的标识
        '''
        rdb = redis.StrictRedis.from_url(MAPREDUCE_URL)
        return rdb.get(cls.REDUCE_TASK_PREFIX + taskid)

    @classmethod
    def delMapCeleryid(cls, taskid):
        '''
        从redis中删除map任务key
        '''
        rdb = redis.StrictRedis.from_url(MAPREDUCE_URL)
        rdb.delete(cls.MAP_TASK_PREFIX + taskid)

    @classmethod
    def delReduceCeleryid(cls, taskid):
        '''
        从redis中删除reduce任务key
        :param taskid:
        '''
        rdb = redis.StrictRedis.from_url(MAPREDUCE_URL)
        rdb.delete(cls.REDUCE_TASK_PREFIX + taskid)

    @classmethod
    def setMapTaskids(cls, taskid, mapids):
        '''
        记录所有属于taskid的map任务标识
        '''
        rdb = redis.StrictRedis.from_url(MAPREDUCE_URL)
        rdb.set(cls.ALL_MAP_TASKS_PREFIX + taskid, ",".join(mapids))

    @classmethod
    def getMapTaskids(cls, taskid):
        '''
        返回所有的map任务标识
        '''
        rdb = redis.StrictRedis.from_url(MAPREDUCE_URL)
        taskids = rdb.get(cls.ALL_MAP_TASKS_PREFIX + taskid)
        if not taskids:
            return []

        return taskids.decode("utf-8").split(",")

    @classmethod
    def remove(cls, taskid):
        '''
        从redis中删除所有与taskid对应的信息
        '''
        rdb = redis.StrictRedis.from_url(MAPREDUCE_URL)
        rdb.delete(cls.MAP_TASK_PREFIX + taskid)
        rdb.delete(cls.REDUCE_TASK_PREFIX + taskid)
        rdb.delete(cls.ALL_MAP_TASKS_PREFIX + taskid)
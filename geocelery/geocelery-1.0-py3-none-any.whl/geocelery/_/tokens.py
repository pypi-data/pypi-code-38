'''
用户提交的每个任务后台都有多个celery任务与之对应，token负责记录管理以上对应关系
'''
import redis
from geocelery._.settings import TOKENS_URL, BATCH_URL


class TaskToken:

    MUTEX_EXCE_PREFIX = "EXECUTE:"   #执行权key：谁先获得这个token谁执行，由获得token的任务将其删除，来阻止其他任务的执行

    CELERY_TASK_PREFIX = "TASKID:" #关联关系key：记录当其任务对应具体的celery任务的id(排队的时候是3个，执行的时候是1个)

    @classmethod
    def check_and_set(cls, taskid, celeryid):
        '''
        同一个任务对应的多个celery任务的互斥管理
        '''
        rdb = redis.StrictRedis.from_url(TOKENS_URL)

        exists = rdb.exists(cls.MUTEX_EXCE_PREFIX + celeryid)  #故障恢复后的任务重试
        if exists:
            return True

        #如果MUTEX_TOKEN_PREFIX+taskid存在，则返回1(获得执行权)，否则返回0(未能获得执行权)
        nums = rdb.delete(cls.MUTEX_EXCE_PREFIX + taskid)
        if nums == 0:
            return False

        #由获得执行权的任务进行初始化设置
        rdb.set(cls.MUTEX_EXCE_PREFIX + celeryid, taskid)  #把原来的token改个名字，可以防止该任务在失败重试时被拒绝
        rdb.set(cls.CELERY_TASK_PREFIX + taskid, celeryid) #记录当前负责执行taskid的celery任务是哪一个

        return True

    @classmethod
    def remove(cls, celeryid):
        '''
        任务执行结束后删除执行权key
        '''
        rdb = redis.StrictRedis.from_url(TOKENS_URL)
        rdb.delete(cls.MUTEX_EXCE_PREFIX + celeryid)

    @classmethod
    def setCeleryids(cls, taskid, celeryids):
        '''
        记录任务(taskid)关联的所有celery任务标识(celeryids数组)
        '''
        rdb = redis.StrictRedis.from_url(TOKENS_URL)
        rdb.set(cls.MUTEX_EXCE_PREFIX + taskid, None)
        rdb.set(cls.CELERY_TASK_PREFIX + taskid, ",".join(celeryids))

    @classmethod
    def getCeleryids(cls, taskid):
        '''
        获取任务(taskid)对应的所有celery任务的标识，需要操作底层任务时调用(如查询状态、获取结果)
        '''
        rdb = redis.StrictRedis.from_url(TOKENS_URL)
        taskids = rdb.get(cls.CELERY_TASK_PREFIX + taskid)
        if not taskids:
            return []
        return taskids.decode("utf-8").split(",")

    @classmethod
    def setMassCeleryids(cls, all_celeryids):
        '''
        批量记录用户任务与celery任务的对应关系(适合map/reduce场景)
        '''
        rdb = redis.StrictRedis.from_url(TOKENS_URL)
        pipe = rdb.pipeline()
        for taskid in all_celeryids:
            celeryids = all_celeryids[taskid]
            pipe.set(cls.MUTEX_EXCE_PREFIX + taskid, None)
            pipe.set(cls.CELERY_TASK_PREFIX + taskid, ",".join(celeryids))
        pipe.execute()

    @classmethod
    def removeAll(cls, taskid):
        '''
        删除redis中所有与taskid关联的信息(终止任务时调用)
        '''
        rdb = redis.StrictRedis.from_url(TOKENS_URL)
        rdb.delete(cls.MUTEX_EXCE_PREFIX + taskid)
        rdb.delete(cls.CELERY_TASK_PREFIX + taskid)


class BatchToken:

    RUNING_TAG = "r"    #正在执行celery任务标识
    COUNTS_TAG = "n"    #已完成的任务数量
    TOTALS_TAG = "t"    #批量任务中的全部任务数量
    REVOKE_TAG = "z"    #判断该批量任务是否已被客户端撤销

    @classmethod
    def reset_token(cls, taskid):
        '''
        设置revoke key，表明该任务已被终止(撤销)
        '''
        rdb = redis.StrictRedis.from_url(BATCH_URL)
        rdb.set(taskid + ":" + cls.REVOKE_TAG, "")

    @classmethod
    def check_revoked_token(cls, taskid):
        '''
        检查有没有撤销标志key，有的话表明该任务已被终止
        '''
        rdb = redis.StrictRedis.from_url(BATCH_URL)
        return rdb.exists(taskid + ":" + cls.REVOKE_TAG)


    @classmethod
    def set_recent_celeryid(cls, taskid, celeryid):
        '''
        记录最近一个被启动的celery任务
        '''
        rdb = redis.StrictRedis.from_url(BATCH_URL)
        rdb.set(taskid + ":" + cls.RUNING_TAG, celeryid)

    @classmethod
    def get_recent_celeryid(cls, taskid):
        '''
        最近一个被启动的celery任务是哪一个
        '''
        rdb = redis.StrictRedis.from_url(BATCH_URL)
        celery_id = rdb.get(taskid + ":" + cls.RUNING_TAG)
        if celery_id:
            return celery_id.decode("utf-8")
        return None


    @classmethod
    def add_finished_count(cls, taskid):
        '''
        增加任务完成数量(+1)
        '''
        rdb = redis.StrictRedis.from_url(BATCH_URL)
        rdb.incr(taskid + ":" + cls.COUNTS_TAG)

    @classmethod
    def get_finished_count(cls, taskid):
        '''
        获取任务已完成的数量
        '''
        rdb = redis.StrictRedis.from_url(BATCH_URL)
        _rst = rdb.get(taskid + ":" + cls.COUNTS_TAG)
        if _rst:
            return int(_rst.decode("utf-8"))
        return None

    @classmethod
    def set_totals(cls, taskid, totals):
        '''
        记录该批量任务包含的总任务量(totals)
        '''
        rdb = redis.StrictRedis.from_url(BATCH_URL)
        rdb.set(taskid + ":" + cls.TOTALS_TAG, totals)

    @classmethod
    def get_totals(cls, taskid):
        '''
        返回该批量任务包含的总任务量
        '''
        rdb = redis.StrictRedis.from_url(BATCH_URL)
        rst = rdb.get(taskid + ":" + cls.TOTALS_TAG)
        if not rst:
            return 0
        return int(rst.decode("utf-8"))
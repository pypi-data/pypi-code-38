# -*- coding: utf-8 -*-
from ..router import router
from .. import debug, info, warn, error
from py_help.api_help.api_wrapper import Api


@Api(router=router, url='py/back_end_task_svr')
def back_end_task(use_gevent=True):
    """att_doc
    @name 启动后台异步任务服务
    @toolable
    @description 启动后台的异步任务服务
    @author woolen
    @params
        use_gevent,name:使用gevent,type:b,required:true,default:true,desc:是否需要加载gevent
    @example
        usage:server back_end_task ,desc:启动后台任务
    @expect 成功|失败|NONE
    """
    from ..backend_task import task_scheduler
    try:
        if use_gevent:
            from gevent import monkey
            monkey.patch_all()
    except ImportError as ex:
        warn("你没有gevent的包,无法利用gevent的高性能::{}".format(ex.message))
    task_scheduler.TaskScheduler.run_service()


@Api(router=router, url='py/trigger_task')
def trigger_task(**kwargs):
    """
    @name 触发运行任务
    @toolable
    @description 触发运行一个任务
    @author 王沃伦
    @params
        url,name:任务url,type:s,required:true,desc:请求的url
        params_key,name:参数key,type:s,desc:需要请求的参数名字,用@隔开
        params_value,name:参数value,type:s,desc:需要请求的参数值,用@隔开
    @example
        usage:py trigger_task --url=tasks/test_task --params_key=is_force --params_value=test,desc:测试触发一下test_task
    @expect 成功|失败|NONE
    """
    from ..backend_task.task_scheduler import TaskScheduler
    the_url = kwargs.get('url')
    if kwargs.get('params_key'):
        keys = kwargs.get('params_key', '').split('@')
        values = kwargs.get('params_value', '').split('@')
        kw_args = dict(zip(keys, values))
    else:
        kw_args = {}
    ret = TaskScheduler.send_task_get_result(1, the_url, kw_args)
    if ret == '__mark_unable_to_send_task_url__':
        return router.fail_msg("无法触发任务,您看是不是后台服务没有起来? url:{}".format(the_url))
    return router.ok_msg("触发返回::{}".format(ret))

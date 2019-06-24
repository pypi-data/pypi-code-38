
# python实例的缓存
from api.exceptions import IllegalArgumentException
from api.handler.IHandler import IHandler
from api.handler.ce.AbstractBatchCE import AbstractBatchCE
from api.handler.ce.ISampleScriptCE import ISampleScriptCE
from api.handler.crawl.AbstractBatchCrawl import AbstractBatchCrawl
from api.handler.crawl.AbstractSimpleCrawl import AbstractSimpleCrawl
from api.handler.crawl.ISampleScriptCrawl import ISampleScriptCrawl
from api.handler.ce.ISimpleScriptCE import ISimpleScriptCE
from api.handler.crawl.ISimpleScriptCrawl import ISimpleScriptCrawl


PYTHON_INSTANCE_CACHE = {}

def _is_subclass(v,clazz)->bool:
    cc = None
    if clazz=="ISimpleScriptCE":
        cc = ISimpleScriptCE
    elif  clazz=="ISimpleScriptCrawl":
        cc = ISimpleScriptCrawl
    elif clazz == "ISampleScriptCE":
        cc = ISampleScriptCE
    elif clazz == "ISampleScriptCrawl":
        cc = ISampleScriptCrawl
    elif clazz == "AbstractBatchCE":
        cc = AbstractBatchCE
    elif clazz == "AbstractBatchCrawl":
        cc = AbstractBatchCrawl
    elif clazz == "AbstractSimpleCrawl":
        cc = AbstractSimpleCrawl
    elif clazz == "IHandler":
        cc = IHandler

    if cc is None:
        return False
    return issubclass(v,cc)

def _find_class(context:dict,clazz):
    script_class = None
    for k, v in context.items():
        if k != clazz and isinstance(v, type) and _is_subclass(v,clazz):
            script_class = v
    return script_class

def load_instance(name:str, code_source:str,clazz):
    if  name in PYTHON_INSTANCE_CACHE:
        # 说明在缓存中,直接返回
        return PYTHON_INSTANCE_CACHE[name]

    # 说明还没有实例化,
    if code_source is None or len(code_source)==0:
        raise IllegalArgumentException(f"加载{name} 失败,源码为空")
    else:
        # 说明是有东西的,开始尝试加载
        context = {}
        from api.model.FdInputPipe import FdInputPipe
        from api.model.BatchOutputPipe import BatchOutputPipe

        context["ISimpleScriptCrawl"] = ISimpleScriptCrawl
        context["ISimpleScriptCE"] = ISimpleScriptCE
        context["ISampleScriptCrawl"] = ISampleScriptCrawl
        context["ISampleScriptCE"] = ISampleScriptCE
        context["AbstractBatchCE"] = AbstractBatchCE
        context["AbstractBatchCrawl"] = AbstractBatchCrawl
        context["AbstractSimpleCrawl"] = AbstractSimpleCrawl
        context["FdInputPipe"] = FdInputPipe
        context["BatchOutputPipe"] = BatchOutputPipe

        # 动态加载源码
        exec(code_source.strip(), context)  # None

        # 找到类定义
        script_class = _find_class(context,clazz)

        if  script_class is None:
            # 说明没有找到,报错
            raise IllegalArgumentException(f"加载{name}的源码失败,没有继承自ISimpleScriptCE/ISimpleScriptCrawl")

        # 放入缓存
        PYTHON_INSTANCE_CACHE[name] = script_class()

        # 返回结果
        return PYTHON_INSTANCE_CACHE[name]

def destroy_instance(name:str):
    """
    清理实例
    :param name:
    :return:
    """
    if  name in PYTHON_INSTANCE_CACHE:
        # 如果存在,就销毁掉
        tmp = PYTHON_INSTANCE_CACHE[name]
        del PYTHON_INSTANCE_CACHE[name]
        del tmp

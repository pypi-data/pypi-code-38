# 日志文件写入器

# 本地log
import logging
import os
import threading
from datetime import datetime

from munch import Munch

local_log = logging.getLogger('Ficus')

# TODO 这里可能有问题,python中还没找到能在子线程中继承的threadLocal,也就是类似JAVA中InheritableThreadLocal的东西
__context_holder = threading.local()

__log_base_path = "/sobeyHiveLogs/sdcLog/JOB/"

def init_log_path(log_path: str):
    global __log_base_path
    if log_path is not None and log_path.strip() != "":
        __log_base_path = log_path

    # 创建文件夹
    if not os.path.exists(__log_base_path):
        try:
            os.makedirs(__log_base_path, exist_ok=True)
        except Exception as e:
            local_log.error(f"初始化日志路径:{__log_base_path} 失败,{str(e)}")
            raise e


def get_log_path() -> str:
    return __log_base_path


def prepare_to_log(trigger_date: datetime, log_id):
    __context_holder.key = _make_log_file_name(trigger_date, log_id)


def end_log():
    __context_holder.key = None


def get_log_file_name() -> str:
    return __context_holder.key


def get_log_file_path(trigger_date: datetime, log_id) -> str:
    return os.path.join(get_log_path(), trigger_date.strftime("%Y-%m-%d"), (str(log_id) if log_id is not None else "0")+".log")


def _make_log_file_name(trigger_date: datetime, log_id):
    dir_path = os.path.join(get_log_path(), trigger_date.strftime("%Y-%m-%d"))

    if not os.path.exists(dir_path):
        try:
            os.mkdir(dir_path)
        except OSError as e:
            import errno
            if e.errno != errno.EEXIST:
                local_log.error(f"创建日志路径{dir_path}失败,{str(e)}")
                raise

    #  filePath/yyyy-MM-dd/9999.log
    return os.path.join(dir_path, (str(log_id) if log_id is not None else "0")+".log")


def append_log(log_file_name: str, append_log: str):
    """
    追加方式写文件
    :param log_file_name:
    :param append_log:
    :return:
    """
    if log_file_name is None or log_file_name.strip() == "":
        return

    append_log = append_log if append_log is not None else ""

    with open(log_file_name,"a+",encoding="utf-8") as file:
        try:
            file.writelines([append_log,"\n"])
        except Exception as e:
            local_log.error(f"写文件失败,{str(e)}")



def read_log(instance_address:str,trigger_date: datetime, log_id, from_line_num: int, to_line_num: int)->Munch:
    """
    读取文件内容
    :param trigger_date:
    :param log_id:
    :param from_line_num:
    :param to_line_num:
    :return:
    """
    log_file_path = get_log_file_path(trigger_date,log_id)

    if not os.path.exists(log_file_path):
        munch = Munch()
        munch.fromLineNum = from_line_num
        munch.toLineNum = to_line_num
        munch.instanceAddress = instance_address
        munch.content = f"无日志输出或日志文件已清除({log_file_path})"
        munch.end = True
        return munch

    # 这个是文件存在
    with open(log_file_path,"rt",encoding="utf-8") as file:
        logContentBuffer = []
        _toLineNum = 0
        # index 0开始
        for index, content in enumerate(file):
            _toLineNum = index

            if to_line_num >0 and _toLineNum >= to_line_num:
                # 超过了目标,就直接返回了
                munch = Munch()
                munch.fromLineNum = from_line_num
                munch.toLineNum = to_line_num
                munch.content = ''.join(logContentBuffer)
                munch.instanceAddress = instance_address
                munch.end = False
                return munch

            if _toLineNum >= from_line_num:
                logContentBuffer.append(content)

        content = ''.join(logContentBuffer)
        if content.strip()=="":
            content = "文本内容为空"

        munch = Munch()
        munch.fromLineNum = from_line_num
        munch.toLineNum = _toLineNum
        munch.content = content
        munch.end = True
        munch.instanceAddress = instance_address
        return munch
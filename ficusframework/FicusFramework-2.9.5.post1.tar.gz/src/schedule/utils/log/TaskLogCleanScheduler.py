# 定时清除日志文件的定时器
import logging
import os
import re
import shutil
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from config.annotation import Value
from schedule.utils.log import TaskLogFileAppender

scheduler = BackgroundScheduler()

logger = logging.getLogger('Ficus')

class TaskLogCleanScheduler:
    """
    定时清除日志文件的定时器
    """

    @Value("${log.retention.days:3}")
    def log_retention_days(self):
        pass

    @Value("${log.path:/sobeyHiveLogs/sdcLog/JOB/}")
    def base_log_path(self):
        pass

    def __init__(self) -> None:
        TaskLogFileAppender.init_log_path(self.base_log_path())


    def _run_(self):
        """
        清理日志文件
        :return:
        """
        if self.log_retention_days() < 1:
            return

        # 找到日志的目录
        logPath = TaskLogFileAppender.get_log_path()

        logger.info(f"过期日志清除器开始清理:{logPath} 下的超过{self.log_retention_days()}天的日志")

        today = datetime.now()

        try:
            with os.scandir(logPath) as it:
                for entry in it:
                    if re.fullmatch(r"\d{4}-\d{2}-\d{2}",entry.name) is not None:
                        # 找到文件夹了
                        fileName = entry.name
                        try:
                            logFileCreateDate = datetime.strptime(fileName,"%Y-%m-%d")
                        except:
                            # 文件名不合法
                            return
                        res = today - logFileCreateDate
                        if res.days>=self.log_retention_days():
                            # 超过了日期了,进行删除
                            shutil.rmtree(entry.path, ignore_errors=True)
                            logger.info(f"过期日志清除器,删除过期日志:{entry.path}")
        except Exception as e:
            logger.error(f"过期日志清除器,清理日志失败.{str(e)}")


    def start(self):
        """
        开启清理定时任务 每天晚上 2点30 执行清除.
        :return:
        """
        if scheduler.get_job("task_log_clean") is None:
            scheduler.add_job(self._run_, 'cron', minute='30',second='0',hour='2',id="task_log_clean")
            scheduler.start()
            return True

        return False

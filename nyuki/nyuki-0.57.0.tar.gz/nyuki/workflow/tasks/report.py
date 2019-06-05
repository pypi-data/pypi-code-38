import logging
from tukio.task import register
from tukio.task.holder import TaskHolder


log = logging.getLogger(__name__)


@register('report', 'execute')
class ReportTask(TaskHolder):

    """
    An base task that can perform some http calls on an API.
    """

    NAME = 'report'

    async def execute(self, event):
        log.info('workflow report data: \033[92m"{}"\033[1;m'.format(event.data))
        return event.data
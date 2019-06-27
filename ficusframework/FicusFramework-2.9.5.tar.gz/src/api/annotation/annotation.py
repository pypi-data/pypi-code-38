"""
注解类,用于表名Taskhandler的注解的,TODO 这里肯定是错的
"""

TASK_HANDLERS = dict()


def TaskHandler(name):
    """
    TaskHandler的类注解
    :param name:
    :return:
    """

    def decorate(cls):
        TASK_HANDLERS[name] = cls()

    return decorate

import inspect
import logging
import logging.config
import logging.handlers as handlers
import os


class RelativePathRotatingFileHandler(handlers.RotatingFileHandler):
    def __init__(self, relative_path, file_name, max_bytes=2000, backup_count=100):
        local_path = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(local_path, relative_path)
        if not os.path.isdir(log_path):
            os.mkdir(log_path)
        log_file_name = os.path.join(log_path, file_name)
        super(RelativePathRotatingFileHandler, self).__init__(log_file_name, max_bytes, backup_count)


def get_log_file_name():
    for handler in logging.root.handlers:
        if handler.baseFilename is not None:
            return handler.baseFilename
    return None


def get_logger():
    stack = inspect.stack()
    if len(stack) == 2:
        file_name = os.path.basename(stack[1][1]).split(".")[0]
    else:
        file_name = os.path.basename(stack[2][1]).split(".")[0]
    the_function = stack[1][3]
    # noinspection PyBroadException
    try:
        if len(stack[1][0].f_locals) > 0:
            the_class = str(stack[1][0].f_locals["self"].__class__.__name__) + "."
        else:
            the_class = ""
    except Exception:
        the_class = ""
    logger_name = "{}.{}{}".format(file_name, the_class, the_function)
    return logging.getLogger(logger_name)


def _get_arg_list(kwargs):
    string = None
    count = 0
    if len(kwargs) == 1:
        # noinspection PyBroadException
        try:
            string = kwargs["msg"]
        except Exception:
            pass
    if string is None:
        string = ""
        for key in kwargs:
            val = kwargs[key]
            string += str(key) + "=" + str(val)
            if count < len(kwargs) - 1:
                string += ","
                count += 1
    return string


def start_function(logger, **kwargs):
    stack = inspect.stack()
    the_function = stack[1][3]
    logger.debug("Starting {}({})".format(the_function, _get_arg_list(kwargs)))


def end_function(logger, **kwargs):
    stack = inspect.stack()
    the_function = stack[1][3]
    logger.debug("Ending {}({})".format(the_function, _get_arg_list(kwargs)))


def test_function():
    logger = get_logger()
    val1 = 5
    val2 = 6
    start_function(logger, msg="testing")
    start_function(logger, val1=val1, val2=val2)
    val1 = 10
    val2 = {"first": 1, "second": 2}
    end_function(logger, val1=val1, val2=val2)
    print(get_log_file_name())


def main():
    logger = get_logger()
    start_function(logger, msg="starting")
    test_function()


if __name__ == '__main__':
    log_configuration_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logging.conf')
    logging.config.fileConfig(log_configuration_file)
    main()

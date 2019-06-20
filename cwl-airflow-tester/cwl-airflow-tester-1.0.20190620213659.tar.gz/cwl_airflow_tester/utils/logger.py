import logging


LOG_FORMAT = '%(message)s'


def reset_root_logger(level=logging.INFO):
    for log_handler in logging.root.handlers:
        logging.root.removeHandler(log_handler)
    for log_filter in logging.root.filters:
        logging.root.removeFilter(log_filter)
    logging.basicConfig(level=level, format=LOG_FORMAT)

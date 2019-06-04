IS_DEBUG = True

def log(log_data):
    """
    Prints the given string to command line if IS_DEBUG is true
    :param log_data: the data to log
    :return:
    """
    if IS_DEBUG:
        print(log_data)
def faultHandler(func):
    """
        Handles functions with no return.
        Decorated function returns True if function executed successfully, False if something went wrong.
    """
    def wrapper(*args, **kwargs):

        try:
            func(*args, **kwargs);
            return True;

        except Exception as error_message:
            print("Something went wrong: {}".format(error_message));
            return False;

    return wrapper;

##  More of a proof of concept?


def permissions_csr(func):
    """

    :param func:
    :return:
    """
    def func_wrapper(name):
        return "<p>{0}</p>".format(func(name))
    return func_wrapper


def permissions_vsr(func):
    """

    :param func:
    :return:
    """
    def func_wrapper(name):
        return "<p>{0}</p>".format(func(name))
    return func_wrapper


def permissions_company_admin(func):
    """

    :param func:
    :return:
    """
    def func_wrapper(name):
        return "<p>{0}</p>".format(func(name))
    return func_wrapper


def permissions_access_user(func):
    """

    :param func:
    :return:
    """
    def func_wrapper(name):
        return "<p>{0}</p>".format(func(name))
    return func_wrapper
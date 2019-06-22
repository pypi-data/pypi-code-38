import platform

Windows = "Windows"

Linux = "Linux"

Mac = "Darwin"

Java = "Java"

OtherOS = "Other OS"


def get_os_type():
    """
    获取操作系统名称
    :return:
    """
    return platform.system()


def is_windows():
    """
    判断是否是Windows操作系统
    :return:
    """
    return platform.system() == Windows


def is_linux():
    """
    判断是否是Linux操作系统
    :return:
    """
    return platform.system() == Linux


def is_mac():
    """
    判断是否是Mac操作系统
    :return:
    """
    return platform.system() == Mac

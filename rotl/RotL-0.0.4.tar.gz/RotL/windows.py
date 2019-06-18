
def delete_file(file_path):
    """Return the command string to delete a file on a windows system.

    :param str file_path: Path to the file to be deleted.
    :return: The command string.
    :rtype: str
    """
    return 'del "{}"'.format(file_path)


def delete_registry_value(reg_path):
    """Return the command to delete a registry value.

    :param str reg_path: A registry key path + '\\' + registry value
    :return: The command string.
    :rtype: str
    """
    reg_key = reg_path[reg_path.rfind('\\')+1:]
    reg_path = reg_path[:reg_path.rfind('\\')]
    return 'REG DELETE "{}" /v "{}" /f'.format(reg_path, reg_key)


def delete_registry_key(reg_path):
    """Return the command to delete a registry key.

    :param str reg_path: A registry key path that should be deleted (all values).
    :return: The command string.
    :rtype: str
    """
    return 'REG DELETE "{}" /f'.format(reg_path)

def delete_service(service_name, service_path=None):
    """Delete a service from the registry.

    :param str service_name: The name of the service that should be deleted.
    :param str service_path: (optional) Specify the path the the service for file deletion.
    :return: Command string to stop the service and delete it from the registry.
    :rtype: str
    """
    cmd = 'net stop "{}" && '.format(service_name)
    if service_path is not None:
        cmd += delete_file(service_path)
        cmd += ' && '
    cmd += 'SC DELETE "{}"'.format(service_name)
    return cmd

def delete_scheduled_task(task_name):
    """Delete a scheduled task.

    :param str task_name: The name of the scheduled task.
    :return: The command string.
    """
    return 'schtasks /Delete /TN "{}" /F'.format(task_name)

def delete_directory(dir_path):
    """Delete an entire directory.

    :param str dir_path: The path to the directory.
    :return: Command string to delete directory contents and the directory.
    """
    cmd = 'cd "{}" && DEL /F /Q /S * > NUL'.format(dir_path)
    cmd += ' && cd .. && RMDIR /Q /S "{}"'.format(dir_path)
    return cmd

def kill_process_name(process):
    """Kill all running processes by a process name.

    :param str process: The process name
    :return: Command string to delete all process
    """
    return 'taskkill /IM "{}" /F'.format(process)

def kill_process_id(pid):
    """Kill a process by its ID.

    :param str pid: The process ID
    :return: The command string.
    """
    return 'taskkill /F /PID {}'.format(pid)
 

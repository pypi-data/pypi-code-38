
import os
import logging
import configparser

from RotL import windows as win

logger = logging.getLogger(__name__)

REMEDIATION_TYPES = ['files', 'process_names', 'scheduled_tasks', 'services', 'directories', 'pids', 'registry_keys', 'registry_values']

def delete_file(client, file_path):
    """Delete a file on a client.

    :param client: A lerc_api.Client object
    :param str file_path: Path to the file on the client.
    :return: A lerc_api.Command object    
    """
    cmd = client.Run(win.delete_file(file_path))
    logger.info("Issued command:{} to delete '{}' on LERC:{}".format(cmd.id, file_path, client.hostname))
    return cmd

def delete_registry_value(client, reg_path):
    """Delete a registry value on a client.

    :param client: A lerc_api.Client object
    :param str reg_path: A registry key path + '\\' + registry value
    :return: A lerc_api.Command object
    """
    cmd = client.Run(win.delete_registry_value(reg_path))
    logger.info("Issued command:{} to '{}' on LERC:{}".format(cmd.id, cmd.command, client.hostname))
    return cmd

def delete_registry_key(client, reg_path):
    """Delete registry key on a client.

    :param lerc_api.Client client: A LERC Client.
    :param str reg_path: A registry key path that should be deleted (all values).
    :return: A lerc_api.Command
    """
    cmd = client.Run(win.delete_registry_key(reg_path))
    logger.info("Issued command:{} to '{}' on LERC:{}".format(cmd.id, cmd.command, client.hostname))
    return cmd

def delete_service(client, service_name, service_path=None, auto_fill=False):
    """Delete a service from the registry.

    :param lerc_api.Client client: A LERC Client.
    :param str service_name: The name of the service that should be deleted.
    :param str service_path: (optional) Specify the path the the service for file deletion.
    :param bool auto_fill: If True, use wmic to query the client for PathName and State. Stop the service if running, delete the path, then delete the service from the registry.
    :return: A list of commands that were executed
    :rtype: list
    """
    commands = []
    if auto_fill:
        cmd = client.Run('wmic service where \'name like "{}"\' get name,pathname,state /format:list'.format(service_name))
        logger.info("Issued command:{} to get the PathName and State of service '{}' on LERC:{}".format(cmd.id, service_name, client.hostname))
        cmd.wait_for_completion()
        results = cmd.get_results(return_content=True)
        if results is None:
            logger.warn("Expected results for wmic service query command:{}".format(cmd.id))
        else:
            results = results.decode('utf-8')
            # for every none-empty line in the results string
            for line in [l for l in results.split('\n\n') if l]:
                if 'PathName' in line:
                    # get path from command line execution
                    if '"' in line:
                        service_path = line[len('PathName="'):]
                        service_path = service_path[:service_path.find('"')]
                    else:
                        service_path = line[len('PathName='):]
                        if service_path.find(' ') > 0:
                            # so there is a space without a '"'. lame. Assuming executable.
                            service_path = service_path[:service_path.find('.exe')+4]
                    logger.info("Found service PathName '{}'".format(service_path))
                elif 'State=Running' in line:
                    logger.info("Service is running on LERC:{}".format(cmd.id, cmd.command, client.hostname))
    if service_path is not None:
        # either the user provided a service path or we got it with wmic via auto=True
        # go ahead and make the service file deletion a tuple of what evaluate_remediation_results needs
        commands.append((delete_file(client, service_path), 'files', service_path))
    cmd = client.Run(win.delete_service(service_name))
    logger.info("Issued command:{} to '{}' on LERC:{}".format(cmd.id, cmd.command, client.hostname))
    commands.append(cmd)
    return commands

def delete_scheduled_task(client, task_name):
    """Delete a scheduled task.

    :param lerc_api.Client client: A LERC Client.
    :param str task_name: The name of the scheduled task.
    :return: A lerc_api.Command object
    """
    cmd = client.Run(win.delete_scheduled_task(task_name))
    logger.info("Issued command:{} to '{}' on LERC:{}".format(cmd.id, cmd.command, client.hostname))
    return cmd

def delete_directory(client, dir_path):
    """Delete an entire directory.

    :param lerc_api.Client client: A LERC Client.
    :param str dir_path: The path to the directory.
    :return: A lerc_api.Command object
    """
    cmd = client.Run(win.delete_directory(dir_path))
    logger.info("Issued command:{} to delete '{}' on LERC:{}".format(cmd.id, cmd.command, client.hostname))
    return cmd

def kill_process_name(client, process):
    """Kill all running processes by a process name.

    :param lerc_api.Client client: A LERC Client.
    :param str process: The process name
    :return: A lerc_api.Command object
    """
    cmd = client.Run(win.kill_process_name(process))
    logger.info("Issued command:{} to kill '{}' on LERC:{}".format(cmd.id, process, client.hostname))
    return cmd

def kill_process_id(client, pid):
    """Kill a process by its ID.

    :param lerc_api.Client client: A LERC Client.
    :param str pid: The process ID
    :return: A lerc_api.Command object
    """
    cmd = client.Run(win.kill_process_id(pid))
    logger.info("Issued command:{} to kill '{}' on LERC:{}".format(cmd.id, pid, client.hostname))
    return cmd

def evaluate_remediation_results(cmd, remediation_type, target_value):
    """Evaluate the remediation results for a given command by the type of remediation it is.

    :param lerc_api.Command cmd: The LERC Command to evaluate
    :param str remediation_type: The type of remediation the command represents.
    :param str target_value: The value of the artifact being remediated on the client.
    """
    if remediation_type not in REMEDIATION_TYPES:
        raise ValueError("Invalid remediation type '{}'. Valid types: {}".format(remediation_type, REMEDIATION_TYPES))

    logger.info("Waiting for command:{} - '{}' to COMPLETE..".format(cmd.id, cmd.command))
    cmd.wait_for_completion()
    results = cmd.get_results(return_content=True)
    if remediation_type == 'process_names':
        pname = target_value
        results = results.decode('utf-8') if results is not None else None
        if cmd.status != 'COMPLETE':
            error_message = cmd.get_error_report()['error']
            logger.error('Problem killing {} : {}:{}'.format(pname, cmd.status, error_message))
        elif 'SUCCESS' in results:
            logger.info("'{}' process names killed successfully : {}".format(pname, results))
        else:
            logger.warn("'{}' process names problem killing : {}".format(pname, results))
    elif remediation_type == 'pids':
        pid = target_value
        results = results.decode('utf-8') if results is not None else None
        if cmd.status != 'COMPLETE':
            error_message = cmd.get_error_report()['error']
            logger.error('Problem killing process id {}'.format(pid, cmd.status, error_message))
        elif 'SUCCESS' in results:
            logger.info("process id '{}' killed successfully : {}".format(pid, results))
        else:
            logger.warn("problem killing process id '{}' : {}".format(pid, results))
    elif remediation_type == 'registry_values':
        rkey = target_value
        results = results.decode('utf-8') if results is not None else None
        if cmd.status != 'COMPLETE':
            error_message = cmd.get_error_report()['error']
            logger.error("Problem deleting '{}'".format(rkey, cmd.status, error_message))
        elif 'success' not in results:
            logger.warn("Problem deleting '{}' : {}".format(rkey, results))
        else:
            logger.info("Deleted '{}' : {}".format(rkey, results))
    elif remediation_type == 'registry_keys':
        rkey = target_value
        results = results.decode('utf-8') if results is not None else None
        if cmd.status != 'COMPLETE':
            error_message = cmd.get_error_report()['error']
            logger.error("Problem deleting '{}'".format(rkey, cmd.status, error_message))
        elif 'success' not in results:
            logger.warn("Problem deleting '{}' : {}".format(rkey, results))
        else:
            logger.info("Deleted '{}' : {}".format(rkey, results))
    elif remediation_type == 'files':
        fname = target_value
        if cmd.status != 'COMPLETE':
            error_message = cmd.get_error_report()['error']
            logger.error("Problem deleting '{}'".format(fname, cmd.status, error_message))
        if results is not None:
            logger.warn("Problem deleting '{}' : {}".format(fname, results.decode('utf-8')))
        else:
            logger.info("File '{}' deleted successfully.".format(fname))
    elif remediation_type == 'directories': 
        directory = target_value
        if cmd.status != 'COMPLETE':
            error_message = cmd.get_error_report()['error']
            logger.error("Problem deleting directory '{}' : {}".format(directory, cmd.status, error_message))
        elif results is not None:
            logger.warn("Problem deleting directory '{}' : {}".format(directory, results.decode('utf-8')))
        else:
            logger.info("Successfully deleted '{}'.".format(directory))
    elif remediation_type == 'scheduled_tasks':
        task = target_value
        results = results.decode('utf-8') if results is not None else None
        if cmd.status != 'COMPLETE':
            error_message = cmd.get_error_report()['error']
            logger.error("Problem deleting scheduled task '{}' : {}: {}".format(task, cmd.status, error_message))
        elif 'SUCCESS' in results:
            logger.info("Scheduled task '{}' deleted successfully : {}".format(task, results))
        else:
            logger.warn("Problem deleting scheduled task '{}' : {}".format(task, results))
    elif remediation_type == 'services':
        service_name = target_value
        results = results.decode('utf-8') if results is not None else None
        if cmd.status != 'COMPLETE':
            error_message = cmd.get_error_report()['error']
            logger.error("Problem remediating service '{}' : {}: {}".format(service_name, cmd.status, error_message))
        elif 'service was stopped successfully' in results:
            logger.info("The '{}' service was stopped successfully.".format(service_name))
        elif 'DeleteService SUCCESS' in results:
            logger.info("The '{}' service was successfully deleted from the registry.".format(service_name))
        else:
            logger.warn("Problem remediating service '{}' : command:{}".format(service_name, cmd.id))
    else:
        logger.error("Unexpected remediation evaluation : command_id={} - {} - {}".format(cmd.id, remediation_type, target_value))


def Remediate(client, remediation_script):
    """Perform a remediation effort on a client via a remediation configuration script.

    :param lerc_api.Client client: The LERC Client
    :param str remediation_script: The path to the remediation config file.
    """
    if not os.path.exists(remediation_script):
        logger.error("'{}' Does not exist".format(remediation_script))
        return False
    logger.info("Attempting to perform mass remediation via '{}' on LERC:{}".format(remediation_script, client.hostname))

    config = configparser.ConfigParser()
    config.read(remediation_script)

    commands = {'files': [],
                'process_names': [],
                'scheduled_tasks': [],
                'directories': [],
                'pids': [],
                'registry_keys': [],
                'registry_values': [],
                'services': []}

    # Order matters
    processes = config['process_names']
    for p in processes:
        commands['process_names'].append(kill_process_name(client, processes[p]))

    pids = config['pids']
    for p in pids:
        commands['pids'].append(kill_process_id(client, pids[p]))

    regValues = config['registry_values']
    for key in regValues:
        commands['registry_values'].append(delete_registry_value(client, regValues[key]))

    regKeys = config['registry_keys']
    for key in regKeys:
        commands['registry_keys'].append(delete_registry_key(client, regKeys[key]))

    files = config['files'] 
    for f in files:
        commands['files'].append(delete_file(client, files[f]))

    dirs = config['directories']
    for d in dirs:
        commands['directories'].append(delete_directory(client, dirs[d]))

    tasks = config['scheduled_tasks']
    for t in tasks:
        commands['scheduled_tasks'].append(delete_scheduled_task(client, tasks[t]))

    services = config['services']
    for s in services:
        commands['services'].append(delete_service(client, services[s]))

    # evaluate results and report
    for cmd in commands['process_names']:
        cmd_pname = cmd.command[cmd.command.find('"')+1:cmd.command.rfind('"')]
        # get the process name that is killed in this command, should be single results
        pname = [p for p in [processes[p] for p in processes] if p == cmd_pname][0]
        evaluate_remediation_results(cmd, 'process_names', pname)

    for cmd in commands['pids']:
        pid = [p for p in [pids[p] for p in pids] if p in cmd.command][0]
        evaluate_remediation_results(cmd, 'pids', pid)

    for cmd in commands['registry_values']:
        # get rkey that has path and key in cmd.command
        _cmd_str = cmd.command
        rvalue = [r for r in [regValues[r] for r in regValues] if r[r.rfind('\\')+1:] in _cmd_str and r[:r.rfind('\\')] in _cmd_str][0]
        evaluate_remediation_results(cmd, 'registry_values', rvalue)

    for cmd in commands['registry_keys']:
        rkey = [r for r in [regKeys[r] for r in regKeys] if r in cmd.command][0]
        evaluate_remediation_results(cmd, 'registry_keys', rkey)

    for cmd in commands['files']:
        fname = [f for f in [files[f] for f in files] if f in cmd.command][0]
        evaluate_remediation_results(cmd, 'files', fname)

    for cmd in commands['directories']:
        directory = [d for d in [dirs[d] for d in dirs] if d in cmd.command][0]
        evaluate_remediation_results(cmd, 'directories', directory)

    for cmd in commands['scheduled_tasks']:
        task = [t for t in [tasks[t] for t in tasks] if t in cmd.command][0]
        evaluate_remediation_results(cmd, 'scheduled_tasks', task)

    # services are a tuple list of commands
    for cmds in commands['services']:
        for cmd in cmds:
            if isinstance(cmd, tuple):
                evaluate_remediation_results(cmd[0], cmd[1], cmd[2])
            else:
                service_name = [s for s in [services[s] for s in services] if s in cmd.command][0]
                evaluate_remediation_results(cmd, 'services', service_name)

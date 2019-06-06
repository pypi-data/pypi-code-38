import logging
import re
import time
import datetime
import yaml
import click
from snakebox import customlogging
from subprocess import check_output, CalledProcessError

customlogging.initLogger()
logger = logging.getLogger("snakebox")

defaults = {
    'start_delay': -1,
    'debug': False,
    'vmlist': None,
    'vmfile': None,
    'force': False,
    'max_wait_time': 1.0,
    'add': True,
    'restart': True
}


@click.group()
@click.option('--debug', is_flag=True, default=None)
@click.option('--vmlist',
              help="comma separated list of VMs (default is 'all')",
              type=str,
              nargs=1)
@click.option('--vmfile',
              help="path to vmfile (line by line list of VM names in VirtualBox)",
              type=str,
              nargs=1)
@click.option('-c','--config',
              help="point to config yaml.  Default name is settings.yml and read automatically",
              type=str,
              nargs=1,
              default="settings.yml")
@click.pass_context
def cli(ctx, **kwargs):

    options = defaults.copy()

    try:
        with open(kwargs['config'], 'r') as stream:
            #options = yaml.safe_load(stream)
            options.update(yaml.safe_load(stream))
    except Exception as e:
        if not kwargs['config'] == "settings.yml":
            logger.critical("Failed to load config file: " + kwargs['config'] + " due to error: " + str(e))
            exit(2)
        #options = {}

    options = set_options(options, kwargs)
    logger.setLevel(logging.DEBUG if options['debug'] else logging.INFO)

    vmlist = []
    if options['vmlist']:
        vmlist.extend([v.strip().replace("\"", "") for v in options['vmlist'].split(",")])
    if options['vmfile']:
        from_file = read_vms_from_file(options['vmfile'])
        for v in from_file:
            if v not in vmlist: vmlist.append(v)

    options['vmlist'] = get_current_vmlist() if not vmlist else vmlist
    ctx.obj = options


@cli.command()
@click.pass_context
@click.option('--start-delay',
              help="waiting period between VM startups [min]",
              type=int,
              nargs=1,
              default=None)
def start(ctx, **kwargs):
    options = set_options(ctx.obj, kwargs)
    logger.info("Starting all virtualmachines... ")
    logger.info("Parameters: ")
    logger.info(options)

    start_delay = options['start_delay']
    vmlist = filter_vmlist(ctx.obj['vmlist'], "halted", True)
    for vm in vmlist:
        success = start_single_vm(vm)
        if len(vmlist) > 1 and vm != vmlist[-1] and success and start_delay != -1.0:
            for i in range(start_delay):
                logger.info("Sleeping for " + str(start_delay) + " minutes, " + str(start_delay - i) + " remaining... ")
                time.sleep(1)
    logger.info("Finished boot sequence for all VM's!")


@cli.command()
@click.pass_context
@click.option('--force', is_flag=True, default=None,
              help="how to power down the vm - hard (force) or normal (acpi)")
def stop(ctx, **kwargs):
    options = set_options(ctx.obj, kwargs)
    logger.info("Stopping all virtualmachines... ")
    logger.info("Parameters: ")
    logger.info(options)

    vmlist = filter_vmlist(options['vmlist'], "running", True)
    stop_all(vmlist, force=options['force'])
    logger.info("Finished shutdown sequence for all VM's!")


@cli.command()
@click.pass_context
@click.option('--force', is_flag=True,
              help="how to power down the vm - hard (force) or normal (acpi)")
@click.option('--max-wait-time',
              help="restart will continue after this time (minutes) even if some VM's did not shut down.  Use 0 for never.",
              type=float,
              nargs=1,
              default=None)
def restart(ctx, **kwargs):
    options = set_options(ctx.obj, kwargs)
    logger.info("Restarting virtualmachines... ")
    logger.info("Parameters: ")
    logger.info(options)

    max_wait_time = float(options['max_wait_time']) * 60.0
    vmlist = filter_vmlist(options['vmlist'], filter="running", exit_on_empty=True)

    if options['force']:
        for vm in vmlist:
            hard_reset_vm(vm)
    else:
        stop_all(vmlist, max_wait=max_wait_time)
        start_all(vmlist)

    logger.info("Finished reboot sequence for all VM's!")


@cli.command()
@click.pass_context
@click.option('--force', is_flag=True, default=None,
              help="how to power down the vm - hard (force) or normal (acpi)")
@click.option('--add', is_flag=True, default=None,
              help="if set, the VM will be registered in the virtualbox GUI afterwards")
@click.option('--restart', is_flag=True, default=None,
              help="if set, the original VMs will be started after cloning")
def clone(ctx, **kwargs):
    options = set_options(ctx.obj, kwargs)
    logger.info("Cloning virtualmachines... ")
    logger.info("Parameters: ")
    logger.info(options)

    max_wait_time = float(options['max_wait_time']) * 60.0
    vmlist_run = filter_vmlist(options['vmlist'], filter="running")

    stop_all(vmlist_run, options['force'], max_wait_time)
    for vm in options['vmlist']:
        clone_single_vm(vm, options['add'])

    if options['restart']:
        logger.info("Restart was True - starting up VM's... ")
        start_all(options['vmlist'])

    logger.info("Clone operation finished!")


def await_vm_halt(vmlist, max_wait):
    if max_wait == -1.0: return True
    start_time = time.time()
    time.sleep(2)
    count = 0
    while True:
        elapsed_time = time.time() - start_time
        remaining = filter_vmlist(vmlist, "running")
        if len(remaining) == 0:
            return True

        if elapsed_time > max_wait and max_wait != 0:
            logger.info("Max wait time exceeded.. continuing on startup... ")
            return False
        else:
            left = "inf" if max_wait == 0 else str(round(max_wait - elapsed_time))
            logger.info("Waiting for VM's to power down, " + left + " seconds remaining... " + str(remaining))
            count += 1
            if count % 5 == 0:
                logger.info("Retrying stop command...")
                stop_all(vmlist, max_wait=-1)
            time.sleep(5)


def filter_vmlist(vmlist, filter, exit_on_empty=False):
    logger.debug("Filtering vm list, and returning all that are: " + filter)
    logger.debug("Starting VM list: " + str(vmlist))

    updated_list = list(vmlist)
    running = get_running_vms()
    if filter == "running":
        for v in vmlist:
            if v not in running:
                logger.info("Skipping " + v + ", already stopped!")
                updated_list.remove(v)
    else:
        for v in running:
            if v in vmlist:
                logger.info("Skipping " + v + ", already running!")
                updated_list.remove(v)

    if len(updated_list) == 0 and exit_on_empty:
        logger.debug("No VM's left in list!! exiting!")
        exit(0)

    logger.debug("Filtered VM list: " + str(updated_list))
    return updated_list


def set_options(options, commandline):
    for key in commandline:
        if key not in options or commandline[key]:
            options[key] = commandline[key]
        if not options[key]:
            options[key] = defaults[key]
    return options


def read_vms_from_file(path):
    try:
        filtered = []
        raw = [line.rstrip('\n').rstrip('\r') for line in open(path)]
        for l in raw:
            if l and not l.startswith("#"): filtered.append(l)
        return filtered

    except Exception as e:
        logger.critical("Error in reading VM file file! Process will terminate! Error: " + str(e))
        exit(2)


def get_running_vms():
    logger.debug("Fetch running VM's... ")
    running = parse_vm_list(shell_exec("vboxmanage list runningvms")[0])
    return running if running else []


def hard_reset_vm(name):
    logger.info("Attempting to hard restart vm: " + name)
    r, c = shell_exec("vboxmanage controlvm \"" + name + "\" reset")
    if not c: logger.warning("Failed to restart vm: " + name)
    return c


def stop_all(vmlist, force=False, max_wait=-1.0):
    for vm in vmlist:
        stop_single_vm(vm, force=force)
    return await_vm_halt(vmlist, max_wait=max_wait)


def start_all(vmlist):
    for vm in vmlist:
        start_single_vm(vm)


def process_shell_result(command, fail_message):
    r, c = shell_exec(command)
    logger.info(r)
    if not c: logger.warning(fail_message)
    return c


def clone_single_vm(name, add=True):
    register = '--register' if add else ''
    cname = name + "_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    logger.info("Attempting to clone vm: " + name)
    return process_shell_result("vboxmanage clonevm \"" + name + "\" --name \"" + cname + "\" " + register, "Failed to clone vm: " + name)


def start_single_vm(name):
    logger.info("Attempting to start vm: " + name)
    return process_shell_result("vboxmanage startvm \"" + name + "\" --type headless", "Failed to boot vm: " + name)


def stop_single_vm(name, force=False, max_wait=-1.0):
    method = "poweroff" if force else "acpipowerbutton"
    logger.info("Attempting to stop vm: " + name)
    c = process_shell_result("vboxmanage controlvm \"" + name + "\" " + method + " --type headless", "Failed to stop vm: " + name)
    await_vm_halt(name, max_wait)
    return c


def get_current_vmlist():
    raw_list, e = shell_exec("vboxmanage list vms")
    if not e:
        logger.critical("Failed to get vmlist, error code: " + str(e) + "! Aborting...")
        exit(2)
    return parse_vm_list(raw_list)


def parse_vm_list(raw):
    return re.findall('(?<=")[^\\\\\n"]+?(?=")', raw)


def shell_exec(cmd):
    logger.debug("Executing: " + cmd)
    try:
        r = format_string(check_output(cmd))
        for s in r.split("\n"):
            logger.debug(s)
        return (r, True)
    except (CalledProcessError, WindowsError) as e:
        r = str(e)
        logger.warning(r)
        return (r, False)


def format_string(string):
    try:
        string = str(string.decode()).strip()
    except TypeError:
        string = str(string).strip()
    return string.strip().replace("\r\n", "\n")


if __name__ == '__main__':
    cli(obj={})

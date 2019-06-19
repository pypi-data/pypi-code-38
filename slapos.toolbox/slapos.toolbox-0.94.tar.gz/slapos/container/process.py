# -*- coding: utf-8 -*-

import os
import subprocess
import logging
import signal

class SlapContainerError(Exception):
    """This exception is thrown, if there is
    any failure during slapcontainer preparation,
    starting or stopping process"""



def main(sr_directory, partition_list, database, bridge_name):

    logger = logging.getLogger('process')

    ######################
    # Process partitions #
    ######################
    start_requested = set()
    logger.debug('Processing partitions...')
    for partition_path in partition_list:
        partition_logger = logger.getChild(
            os.path.basename(partition_path)
        )
        partition_logger.debug('Processing...')

        # XXX: Hardcoded path
        slapcontainer_filename = os.path.join(partition_path,
                                              '.slapcontainername')
        if os.path.isfile(slapcontainer_filename):
            partition_logger.debug('Container found...')
            with open(slapcontainer_filename, 'r') as slapcontainer_file:
                name = slapcontainer_file.read().strip()

            # XXX: Hardcoded path
            lxc_conf_path = os.path.join(partition_path,
                                         'etc/lxc.conf')
            lxc_state_path = os.path.join(partition_path,
                                          '.slapcontainer.state')
            sib_state_path = os.path.join(partition_path,
                                          '.shellinabox.state')
            # XXX: Avoid hacking slapos.core
            ##########################################################
            magic_string = '!!BRIDGE_NAME!!'
            with open(lxc_conf_path, 'r') as lxc_conf_file:
                lxc_conf_content = lxc_conf_file.read()
            if magic_string in lxc_conf_content:
                with open(lxc_conf_path, 'w') as lxc_conf_file:
                    lxc_conf_file.write(
                        lxc_conf_content.replace(magic_string, bridge_name)
                    )
            ##########################################################
            with open(lxc_conf_path, 'r') as lxc_conf_file:
                requested_status = lxc_conf_file.readline().strip(' \n\r\t#')

            if requested_status == 'started':
                start_requested.add(name)

            process_partition(requested_status=requested_status,
                              sr_directory=sr_directory,
                              partition_path=partition_path,
                              name=name,
                              database=database,
                              logger=partition_logger,
                              lxc_conf_filename=lxc_conf_path,
                              lxc_state_path=lxc_state_path,
                              sib_state_path=sib_state_path)

    if start_requested:
        logger.debug('Container which start was requested : %s.',
                     ', '.join(start_requested))


    ####################################
    # Stop unwanted running containers #
    ####################################
    try:
        active_containers = set((container.strip() for container in call(
            [os.path.join(sr_directory, 'parts/lxc/bin/lxc-ls'),
             '--active']
        ).split('\n') if container.strip()))
        logger.debug('Active containers are %s.', ', '.join(active_containers))
    except SlapContainerError:
        active_containers = set()

    ### Stop containers
    to_stop = active_containers - start_requested
    if to_stop:
        logger.debug('Stopping containers %s.', ', '.join(to_stop))
    else:
        logger.debug('No extra containers to stop.')

    for container in to_stop:
        try:
            logger.info('Stopping container %s.', container)
            call(
                [os.path.join(sr_directory, 'parts/lxc/bin/lxc-stop'),
                 '-n', container
                ]
            )
        except SlapContainerError:
            logger.fatal('Impossible to stop %s.', container)

    ### Stop shellinaboxes
    active_shellinabox = set(database.keys())
    to_stop = active_shellinabox - start_requested
    if to_stop:
        logger.debug('Stopping shellinaboxes %s.', ', '.join(to_stop))
    else:
        logger.debug('No extra shellinabox to stop.')

    for shellinabox in to_stop:
        pid = int(database[shellinabox])
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            # Shellinabox's already stopped
            del database[shellinabox]
        else:
            # Stopping shellinabox
            if not is_pid_running(pid):
                del database[shellinabox]



def process_partition(requested_status,
                      sr_directory,
                      partition_path,
                      name,
                      database,
                      logger,
                      lxc_conf_filename,
                      lxc_state_path,
                      sib_state_path):

    if requested_status == 'started':

        ##############################
        # Stateless container launch #
        ##############################

        logger.debug('Check status.')
        lxc_info = call([os.path.join(sr_directory, 'parts/lxc/bin/lxc-info'),
                         '-n', name])
        ### Check if container is launched
        if 'RUNNING' in lxc_info:
            current_status = 'started'
        else:
            current_status = 'stopped'

        with open(lxc_state_path, 'w') as lxc_state_file:
            lxc_state_file.write(current_status)

        ### If container is not launch, launch it
        if requested_status != current_status:
            logger.debug('Start lxc.')
            lxc_start = os.path.join(sr_directory,
                                     'parts/lxc/bin/lxc-start')
            call([lxc_start, '-f', lxc_conf_filename,
                  '-n', name,
                  '-d'])

        ################################
        # Stateless shellinabox launch #
        ################################

        current_status = 'stopped'
        # Check if shellinabox is started
        if name in database:
            pid = int(database[name])
            if is_pid_running(pid):
                current_status = 'started'
        with open(sib_state_path, 'w') as sib_state_file:
            sib_state_file.write(current_status)

        if current_status == 'stopped':
            logger.debug('Start shellinabox.')
            shellinabox_pid = call_daemonize([os.path.join(partition_path,
                                                           'bin/shellinaboxd')])
            database[name] = str(shellinabox_pid)



def is_pid_running(pid):
    logger = logging.getLogger('pid')
    logger.debug('Check if pid %d is running.', pid)
    # XXX: Magic number 0 for no special signal
    try:
        os.kill(pid, 0)
        logger.debug('%d is running.', pid)
        return True
    except OSError:
        # Process doesn't exists
        logger.debug('%d is not running.', pid)
        return False

def call(command_line, override_environ={}):
    logger = logging.getLogger('commandline')
    logger.debug('Call %s', ' '.join(command_line))

    environ = dict(os.environ)
    environ.update(override_environ)
    process = subprocess.Popen(command_line, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, env=environ)
    process.stdin.flush()
    process.stdin.close()

    if process.wait() != 0:
        logger.debug('Failed')
        raise SlapContainerError("Subprocess call failed")

    out = process.stdout.read()
    logger.debug('Output : %s.', out)
    return out



def call_daemonize(command_line, override_environ={}):
    logger = logging.getLogger('daemon')

    environ = dict(os.environ)
    environ.update(override_environ)

    daemon = subprocess.Popen(command_line, env=environ)
    logger.debug('Daemonize as pid %d : %s', daemon.pid,
                                             ' '.join(command_line))
    return daemon.pid

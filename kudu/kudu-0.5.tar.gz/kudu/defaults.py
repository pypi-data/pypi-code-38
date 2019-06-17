import os
import re
import subprocess

import click


def default_pitcher_folders():
    click.echo('Your Pitcher Folders are configured automatically based on your iOS simulator devices. Please check '
               'that they are accurate. You can suppress this message by setting them explicitly. Run the following '
               'command and follow the instructions in your editor to edit your configuration file:\n\n'
               '\tkudu config --global --edit\n')

    ios_sim_devices = []

    try:
        instruments_output = subprocess.check_output(['instruments', '-s', 'devices']).splitlines()
        prog = re.compile(r"iPad .+\[([^\]]+)")
        devices_path = os.path.expanduser('~/Library/Developer/CoreSimulator/Devices/')

        for line in instruments_output:
            prog_match = prog.match(line)
            if prog_match:
                device_guid = prog_match.group(1)
                find_output = subprocess.check_output(
                    ['find', os.path.join(devices_path, device_guid), '-name', 'Pitcher Folders']).strip()
                if find_output:
                    ios_sim_devices.append({'name': line, 'guid': device_guid, 'pitcher_folders': find_output})
    except OSError:
        pass

    if len(ios_sim_devices) > 0:
        ios_sim_device_index = 0

        if len(ios_sim_devices) > 1:
            for key, device in enumerate(ios_sim_devices):
                click.echo('%d. %s' % (key + 1, device['name']))
            ios_sim_device_index = int(click.prompt('Please select a device', type=click.Choice(
                [str(key + 1) for key, device in enumerate(ios_sim_devices)]))) - 1

        return ios_sim_devices[ios_sim_device_index]['pitcher_folders']

#!/usr/bin/python

"""
Install Systemd units using Ansible
Handles unit restarting and systemd daemon reloading when the unit changes.
Also stops the unit correctly when uninstalled.

Install using pip install ansible-systemd-module

Example:

Use the normal systemd module to start it and enable it on boot
- name: Enable valu-backup service
  systemd: name="example.service" state=started enabled=yes
"""


DOCUMENTATION = '''
module: systemd_service
author:
    - "Moshe Immerman"
short_description:  Creates systemd services
description:
    -  Creates systemd services
options:
    Name:
        required: True
        description: ['']
    ExecStart:
        required: True
        description: ['']
    Description:
        required: false
        default: ''
        description: ['']
    RestartOn:
        required: false
        default: 'on-failure'
        description: ['']
    WantedBy:
        required: false
        default: 'multi-user.target'
        description: ['']
    RunAs:
        required: false
        default: 'root'
        description: ['']
    UnitArgs:
        required: false
        default: ''
        description: ['']
    ServiceArgs:
        required: false
        default: ''
        description: ['']
    InstallArgs:
        required: false
        default: ''
        description: ['']
    state:
        required: False
        default: present
        choices: ['present', 'absent']
        description: ['']
'''
EXAMPLES = '''
     - systemd_service:
          Name: test
          ExecStart: "/usr/bin/nc -l 200"
'''
import os.path
from subprocess import check_call
from ansible.module_utils.basic import AnsibleModule

import logging

logger = logging.getLogger('systemd')
hdlr = logging.FileHandler('/tmp/ansible-systemdunit.log')
logger.addHandler(hdlr)
logger.setLevel(logging.DEBUG)


ROOT = "/etc/systemd/system/"


def systemctl(arg1, arg2=None):
    if arg2 is None:
        check_call(["/bin/systemctl", arg1])
    else:
        check_call(["/bin/systemctl", arg1, arg2])
def present(unit_path, name, content):
    changed = False

    if not os.path.exists(unit_path):
        with open(unit_path, "w") as f:
            f.write(content)
            changed = True
        logger.info("Created new")
    else:
        current = open(unit_path).read()
        if current.strip() != content.strip():
            with open(unit_path, "w") as f:
                f.write(content)
                changed = True
            logger.info("Content changed")

    is_running = False

    try:
        systemctl("is-active", name)
        is_running = True
    except:
        pass

    if changed:
        systemctl("daemon-reload")

    if is_running and changed:
        logger.info("Restarting because changed and is running")
        systemctl("restart", name)

    return changed


def absent(unit_path, name):
    changed = False

    try:
        systemctl("stop", name)
        changed = True
        logger.info("Stopped")
    except:
        pass

    if os.path.exists(unit_path):
        check_call(["/bin/rm", "-f", unit_path])
        systemctl("daemon-reload")
        changed = True
        logger.info("Removed")

    return changed


def main():
    arg_spec = dict(
        Name=dict(required=True),
        Description=dict(default=None),
        ExecStart=dict(required=True),
        Restart=dict(default='on-failure'),
        WantedBy=dict(default='multi-user.target'),
        RunAs=dict(default=None),
        UnitArgs=dict(default=dict(), type='dict'),
        ServiceArgs=dict(default=dict(), type='dict'),
        InstallArgs=dict(default=dict(), type='dict'),
        state=dict(default='present', choices=['present', 'absent']),
    )
    module = AnsibleModule(
        argument_spec=arg_spec,
        supports_check_mode=False
    )

    name = module.params['Name'].strip()
    if name != name.lower():
        return module.fail_json(msg="systemd service names (%s) should be lowercase" % name)

    state = module.params['state']
    unit = module.params['UnitArgs']
    unit['Description'] = module.params['Description']
    service = module.params['ServiceArgs']
    service['ExecStart'] = module.params['ExecStart']
    service['RunAs'] = module.params['RunAs']
    service['Restart'] = module.params['Restart']
    install = module.params['InstallArgs']
    install['WantedBy'] = module.params['WantedBy']

    content = "[Unit]\n"
    for key in unit:
        if unit[key] != None:
            content += "%s=%s\n" % (key, unit[key])

    content += "\n[Service]\n"
    for key in service:
        if service[key] != None:
            content += "%s=%s\n" % (key, service[key])

    content += "\n[Install]\n"
    for key in install:
        if install[key] != None:
            content += "%s=%s\n" % (key, install[key])

    changed = False
    unit_path = ROOT + name + ".service"

    logger.info("Editing systemd unit " + name)

    if state == "present":
        changed = present(unit_path, name, content)
    elif state == "absent":
        changed = absent(unit_path, name)
    else:
        raise Exception("Unknown state param")

    module.exit_json(changed=changed)


if __name__ == '__main__':
    main()
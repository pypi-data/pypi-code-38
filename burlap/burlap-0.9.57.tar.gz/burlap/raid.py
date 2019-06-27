from __future__ import print_function

import re

# from fabric.colors import red, green

from burlap.constants import *
from burlap import Satchel
from burlap.decorators import task
from burlap.common import print_success, print_fail

# This is sample output from `cat /prod/mdstat` after sdb failed and was replaced,
# but not before it was re-added to raid array.
SAMPLE_TEXT_FAILED_SDB = '''
Personalities : [linear] [multipath] [raid0] [raid1] [raid6] [raid5] [raid4] [raid10]
md0 : active raid1 sda1[2]
      7810036 blocks super 1.2 [2/1] [U_]

md1 : active raid1 sda2[2]
      968948600 blocks super 1.2 [2/1] [U_]

unused devices: <none>
'''

ALL_DRIVES_IN_SYSTEM_REGEX = re.compile(r"sd[a-z]")

ALL_DRIVES_IN_ARRAY_REGEX = re.compile(r"sd[a-z]")

ALL_PARTITIONS_IN_ARRAY_REGEX = re.compile(r"([a-zA-Z0-9]+)\[[0-9]+\]")

FAILED_DRIVES_REGEX = re.compile(r"([a-zA-Z0-9]+)\[[0-9]+\]\(F\)")

EMPTY_SLOTS_REGEX = re.compile(r"\[([U_]+)\]")

class SoftwareRaidSatchel(Satchel):

    name = 'softwareraid'

    def set_defaults(self):
        self.env.hdd_replace_description = None

    @task
    def raw_status(self):
        r = self.local_renderer
        ret = r.run('cat /proc/mdstat')
        return ret

    @task
    def status(self):
        r = self.local_renderer

        all_drives_in_system = r.run('ls /dev/sd*')
        all_drives_in_system = set(ALL_DRIVES_IN_SYSTEM_REGEX.findall(all_drives_in_system))
        print('all drives in system:', all_drives_in_system)

        ret = self.raw_status()

        all_drives_in_array = set(ALL_DRIVES_IN_ARRAY_REGEX.findall(ret))
        print('all drives in array:', all_drives_in_array)

        drives_needing_to_be_readded = all_drives_in_system.difference(all_drives_in_array)
        print('drives_needing_to_be_readded:', drives_needing_to_be_readded)

        all_partitions_in_array = set(ALL_PARTITIONS_IN_ARRAY_REGEX.findall(ret))
        print('all partitions in array:', all_partitions_in_array)

        bad_drives = set(FAILED_DRIVES_REGEX.findall(ret))
        print('bad_drives:', bad_drives)

        empty_slots = [_ for _ in EMPTY_SLOTS_REGEX.findall(ret) if '_' in _]
        print('empty_slots:', empty_slots)

        if not all_drives_in_system:
            print_fail('NO DRIVES FOUND! Something is very wrong!')
        if not all_drives_in_array:
            print_fail('NO DRIVES FOUND IN ARRAY! Something is very wrong!')
        elif bad_drives:
            print_fail('RAID has degraded! Shutdown and replace drive:', bad_drives)
        elif empty_slots:
            if drives_needing_to_be_readded:
                drive_str = ', '.join(sorted(drives_needing_to_be_readded))
                print_fail((
                    'RAID has degraded, the failed drive %s has been replaced, '
                    'but it needs to be re-added.') \
                    % drive_str)

                print('''
    # copy partitioning scheme from good drive onto bad drive
    sudo sfdisk -d /dev/{good_drive} | sudo sfdisk /dev/{new_drive}

    # add drive back into raid
    sudo mdadm --manage /dev/md0 --add /dev/{new_drive}1
    sudo mdadm --manage /dev/md1 --add /dev/{new_drive}2

    # wait until drives synced
    cat /proc/mdstat

    #finally install grub on new disk
    sudo grub-install /dev/{new_drive}
                '''.format(**dict(
                    good_drive=list(all_drives_in_array)[0],
                    new_drive=list(drives_needing_to_be_readded)[0],
                )))

            else:
                print_fail('RAID has degraded, the failed drive appears to have been removed, '
                    'but no new drive has been added.')
        else:
            print_success('RAID is good.')

#         print('ret:', ret)

    @task(precursors=['package'])
    def configure(self):
        pass

softwareraid = SoftwareRaidSatchel()

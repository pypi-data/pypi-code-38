# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2018 Vifib SARL and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import unittest
import os
import tempfile
import shutil

from slapos.qemuqmpclient import QemuQMPWrapper, QmpDeviceRemoveError

class TestQemuQMPWrapper(unittest.TestCase):

  def setUp(self):
    self.base_dir = tempfile.mkdtemp()
    self.socket_file = os.path.join(self.base_dir, 'qmp.socket')
    self.call_stack_list = []
    self.free_cpu_slot_amount = 4
    self.hotplugged_memory_amount = 0
    # slot of 1G
    self.memory_slot_size = 1024
    self.event_list = []
    self.fail = False

  def tearDown(self):
    if os.path.exists(self.base_dir):
      shutil.rmtree(self.base_dir)

  def setChange(self, device, value):
    current = self.readChange(device)
    with open(os.path.join(self.base_dir, device), 'w') as f:
      f.write('%s' % (current + value, ))

  def readChange(self, device):
    if os.path.exists(os.path.join(self.base_dir, device)):
      with open(os.path.join(self.base_dir, device)) as f:
        return int(f.read())
    return 0

  def fake_send(self, message, retry=0, sleep=0.5):
    self.call_stack_list.append(message)
    if message.get('execute', '').startswith('query-'):
      return self.returnQueryResult(message)
    elif message.get('execute', '') == 'device_add':
      if message['arguments']['driver'] == 'pc-dimm':
        self.setChange('dimm', self.memory_slot_size)
      elif message['arguments']['driver'] == 'qemu64-x86_64-cpu':
        self.setChange('cpu', 1)
    elif message.get('execute', '') == 'device_del':
      if message['arguments']['id'].startswith('dimm'):
        self.setChange('dimm', -1 * self.memory_slot_size)
      if message['arguments']['id'].startswith('cpu'):
        self.setChange('cpu', -1)
    if self.fail:
      return {"error": {"class": "CommandFailed", "desc": ""}}
    return {"return": {}}

  def fake_getEventList(self, timeout=0, cleanup=False):
    if self.event_list:
      return self.event_list
    else:
      return []

  def returnQueryResult(self, message):
    if message['execute'] == 'query-hotpluggable-cpus':
      # return 4 hotpluggable cpu slots
      hotpluggable_cpu_list = []
      free_cpu_slot = self.free_cpu_slot_amount - self.readChange('cpu')
      for i in range(4, 4 - free_cpu_slot, -1):
        hotpluggable_cpu_list.append({
          u'props': {u'core-id': 0, u'node-id': 0, u'socket-id': i, u'thread-id': 0},
          u'type': u'qemu64-x86_64-cpu',
          u'vcpus-count': 1
        })
      for i in range(4 - free_cpu_slot, 0, -1):
        hotpluggable_cpu_list.append({
          u'props': {u'core-id': 0, u'node-id': 0, u'socket-id': i, u'thread-id': 0},
          u'qom-path': u'/machine/peripheral/cpu%s' % i,
          u'type': u'qemu64-x86_64-cpu',
          u'vcpus-count': 1
        })
      # first cpu
      hotpluggable_cpu_list.append(
        {u'props': {u'core-id': 0, u'node-id': 0, u'socket-id': 0, u'thread-id': 0},
          u'qom-path': u'/machine/unattached/device[0]',
          u'type': u'qemu64-x86_64-cpu',
          u'vcpus-count': 1
        }
      )
      return {"return": hotpluggable_cpu_list}
    elif message['execute'] == 'query-cpus':
      cpu_list = []
      cpu_slot = 4 - self.free_cpu_slot_amount + self.readChange('cpu')
      cpu_list.append({
        u'CPU': 0,
        u'arch': u'x86',
        u'current': True,
        u'halted': True,
        u'pc': -1694470494,
        u'props': {u'core-id': 0, u'node-id': 0, u'socket-id': 0, u'thread-id': 0},
        u'qom_path': u'/machine/unattached/device[0]',
        u'thread_id': 1181
      })
      for i in range(0, cpu_slot):
        cpu_list.append({
          u'CPU': i + 1,
          u'arch': u'x86',
          u'current': False,
          u'halted': True,
          u'pc': -1694470494,
          u'props': {u'core-id': 0, u'node-id': 0, u'socket-id': i + 1, u'thread-id': 0},
          u'qom_path': u'/machine/peripheral/cpu%s' % (i + 1),
          u'thread_id': 1187
        })
      return {"return": cpu_list}
    elif message['execute'] == 'query-memory-devices':
      memory_list = []
      added_mem = self.readChange('dimm') + self.hotplugged_memory_amount
      slot_amount = added_mem / self.memory_slot_size
      for i in range(slot_amount, 0, -1):
        memory_list.append({
          u'data': {
            u'addr': 4563402752,
            u'hotpluggable': True,
            u'hotplugged': True,
            u'id': u'dimm%s' % i,
            u'memdev': u'/objects/mem%s' % i,
            u'node': 0,
            u'size': self.memory_slot_size * 1024 * 1024,
            u'slot': 1
          },
          u'type': u'dimm'
        })
      return {"return": memory_list}
    elif message['execute'] == 'query-memdev':
      memory_list = []
      added_mem = self.readChange('dimm') + self.hotplugged_memory_amount
      slot_amount = added_mem / self.memory_slot_size
      for i in range(slot_amount, 0, -1):
        memory_list.append({
          u'dump': True,
          u'host-nodes': [],
          u'id': u'mem%s' % i,
          u'merge': True,
          u'policy': u'default',
          u'prealloc': False,
          u'size': self.memory_slot_size * 1024 * 1024
        })
      return {"return": memory_list}
    return {"return": {}}

  def test_setVNCPassword(self):
    qmpwrapper = QemuQMPWrapper(self.socket_file, auto_connect=False)
    qmpwrapper._send = self.fake_send

    expected_result = {
      "execute": "change",
      "arguments": {
        "device": "vnc",
        "target": "password",
        "arg": "my password"
      }
    }
    qmpwrapper.setVNCPassword("my password")
    self.assertEqual(len(self.call_stack_list), 1)
    self.assertEqual(self.call_stack_list[0], expected_result)

  def test_updateDevice_cpu_add(self):
    self.free_cpu_slot_amount = 4
    qmpwrapper = QemuQMPWrapper(self.socket_file, auto_connect=False)
    qmpwrapper._send = self.fake_send
    # add 2 cpu
    cpu_option = {
      'device': 'cpu',
      'amount': 2 + 1
    }
    qmpwrapper.updateDevice(cpu_option)
    expected_result = [
      {'execute': 'query-hotpluggable-cpus'},
      {
        'execute': 'device_add',
        'arguments': {
          u'socket-id': 1,
          u'thread-id': 0,
          'driver': 'qemu64-x86_64-cpu',
          u'core-id': 0,
          u'node-id': 0,
          'id': 'cpu1'
        }
      },
      {
        'execute': 'device_add',
        'arguments': {
          u'socket-id': 2,
          u'thread-id': 0,
          'driver': 'qemu64-x86_64-cpu',
          u'core-id': 0,
          u'node-id': 0,
          'id': 'cpu2'
        }
      },
      {'execute': 'query-cpus'}
    ]

    self.assertEqual(len(self.call_stack_list), 4)
    self.assertEqual(self.call_stack_list, expected_result)

  def test_updateDevice_cpu_increase(self):
    self.free_cpu_slot_amount = 2
    qmpwrapper = QemuQMPWrapper(self.socket_file, auto_connect=False)
    qmpwrapper._send = self.fake_send
    # add 2 more cpu
    cpu_option = {
      'device': 'cpu',
      'amount': 4 + 1
    }
    qmpwrapper.updateDevice(cpu_option)
    expected_result = [
      {'execute': 'query-hotpluggable-cpus'},
      {
        'execute': 'device_add',
        'arguments': {
          u'socket-id': 3,
          u'thread-id': 0,
          'driver': 'qemu64-x86_64-cpu',
          u'core-id': 0,
          u'node-id': 0,
          'id': 'cpu3'
        }
      },
      {
        'execute': 'device_add',
        'arguments': {
          u'socket-id': 4,
          u'thread-id': 0,
          'driver': 'qemu64-x86_64-cpu',
          u'core-id': 0,
          u'node-id': 0,
          'id': 'cpu4'
        }
      },
      {'execute': 'query-cpus'}
    ]

    self.assertEqual(len(self.call_stack_list), 4)
    self.assertEqual(self.call_stack_list, expected_result)

  def test_updateDevice_cpu_remove(self):
    self.free_cpu_slot_amount = 2
    qmpwrapper = QemuQMPWrapper(self.socket_file, auto_connect=False)
    qmpwrapper._send = self.fake_send
    qmpwrapper.getEventList = self.fake_getEventList
    self.event_list = [{"event": "DEVICE_DELETED"}]
    # add 2 more cpu
    cpu_option = {
      'device': 'cpu',
      'amount': 1 + 1
    }
    qmpwrapper.updateDevice(cpu_option)
    expected_result = [
      {'execute': 'query-hotpluggable-cpus'},
      {
        'execute': 'device_del',
        'arguments': {
          'id': 'cpu2'
        }
      },
      {'execute': 'query-cpus'}
    ]

    self.assertEqual(len(self.call_stack_list), 3)
    self.assertEqual(self.call_stack_list, expected_result)

  def test_updateDevice_cpu_no_update(self):
    self.free_cpu_slot_amount = 2
    qmpwrapper = QemuQMPWrapper(self.socket_file, auto_connect=False)
    qmpwrapper._send = self.fake_send
    # keep 2 cpu added
    cpu_option = {
      'device': 'cpu',
      'amount': 2 + 1
    }
    qmpwrapper.updateDevice(cpu_option)
    expected_result = [
      {'execute': 'query-hotpluggable-cpus'}
    ]

    self.assertEqual(len(self.call_stack_list), 1)
    self.assertEqual(self.call_stack_list, expected_result)

  def test_updateDevice_memory_add(self):
    self.hotplugged_memory_amount = 0
    qmpwrapper = QemuQMPWrapper(self.socket_file, auto_connect=False)
    qmpwrapper._send = self.fake_send
    # slot of 1G
    self.memory_slot_size = 1024
    # add 2G of RAM = 2 slots to add
    cpu_option = {
      'device': 'memory',
      'nslot': 4,
      'mem': 2048,
      'slot': self.memory_slot_size
    }
    qmpwrapper.updateDevice(cpu_option)
    expected_result = [
      {'execute': 'query-memory-devices'},
      {'execute': 'query-memdev'},
      {
        'execute': 'object-add',
        'arguments': {
          'id': 'mem1',
          'qom-type': 'memory-backend-ram',
          'props': {'size': self.memory_slot_size * 1024 * 1024}
        }
      },
      {
        'execute': 'device_add',
        'arguments': {
          'driver': 'pc-dimm',
          'id': 'dimm1',
          'memdev': 'mem1'
        }
      },
      {
        'execute': 'object-add',
        'arguments': {
          'id': 'mem2',
          'qom-type': 'memory-backend-ram',
          'props': {'size': 1073741824}
        }
      },
      {
        'execute': 'device_add', 
        'arguments': {
          'driver': 'pc-dimm',
          'id': 'dimm2',
          'memdev': 'mem2'
        }
      },
      {'execute': 'query-memory-devices'}
    ]

    self.assertEqual(len(self.call_stack_list), 7)
    self.assertEqual(self.call_stack_list, expected_result)

  def test_updateDevice_memory_increase(self):
    qmpwrapper = QemuQMPWrapper(self.socket_file, auto_connect=False)
    qmpwrapper._send = self.fake_send
    self.hotplugged_memory_amount = 2048
    # slot of 1G
    self.memory_slot_size = 1024
    # increase to 3G, add one more slot of 1G
    cpu_option = {
      'device': 'memory',
      'nslot': 4,
      'mem': 3072,
      'slot': self.memory_slot_size
    }
    qmpwrapper.updateDevice(cpu_option)
    expected_result = [
      {'execute': 'query-memory-devices'},
      {'execute': 'query-memdev'},
      {
        'execute': 'object-add',
        'arguments': {
          'id': 'mem3',
          'qom-type': 'memory-backend-ram',
          'props': {'size': self.memory_slot_size * 1024 * 1024}
        }
      },
      {
        'execute': 'device_add',
        'arguments': {
          'driver': 'pc-dimm',
          'id': 'dimm3',
          'memdev': 'mem3'
        }
      },
      {'execute': 'query-memory-devices'}
    ]

    self.assertEqual(len(self.call_stack_list), 5)
    self.assertEqual(self.call_stack_list, expected_result)

  def test_updateDevice_memory_delete(self):
    qmpwrapper = QemuQMPWrapper(self.socket_file, auto_connect=False)
    qmpwrapper._send = self.fake_send
    qmpwrapper.getEventList = self.fake_getEventList
    self.event_list = [{"event": "DEVICE_DELETED"}]
    self.hotplugged_memory_amount = 3072
    # slot of 1G
    self.memory_slot_size = 1024
    # decrease memory to 1G, expext remove slot 3 and 2.
    cpu_option = {
      'device': 'memory',
      'nslot': 4,
      'mem': 1024,
      'slot': self.memory_slot_size
    }
    qmpwrapper.updateDevice(cpu_option)
    expected_result = [
      {'execute': 'query-memory-devices'},
      {'execute': 'query-memdev'},
      {
        'execute': 'device_del',
        'arguments': {'id': u'dimm3'}
      },
      {
        'execute': 'object-del',
        'arguments': {'id': u'mem3'}
      },
      {
        'execute': 'device_del',
        'arguments': {'id': u'dimm2'}
      },
      {
        'execute': 'object-del',
        'arguments': {'id': u'mem2'}
      },
      {'execute': 'query-memory-devices'}
    ]

    self.assertEqual(len(self.call_stack_list), 7)
    self.assertEqual(self.call_stack_list, expected_result)

  def test_updateDevice_memory_delete_all(self):
    qmpwrapper = QemuQMPWrapper(self.socket_file, auto_connect=False)
    qmpwrapper._send = self.fake_send
    qmpwrapper.getEventList = self.fake_getEventList
    self.event_list = [{"event": "DEVICE_DELETED"}]
    self.hotplugged_memory_amount = 3072
    # slot of 1G
    self.memory_slot_size = 1024
    # remove all hotplugged memory
    cpu_option = {
      'device': 'memory',
      'nslot': 4,
      'mem': 0,
      'slot': self.memory_slot_size
    }
    qmpwrapper.updateDevice(cpu_option)
    expected_result = [
      {'execute': 'query-memory-devices'},
      {'execute': 'query-memdev'},
      {
        'execute': 'device_del',
        'arguments': {'id': u'dimm3'}
      },
      {
        'execute': 'object-del',
        'arguments': {'id': u'mem3'}
      },
      {
        'execute': 'device_del',
        'arguments': {'id': u'dimm2'}
      },
      {
        'execute': 'object-del',
        'arguments': {'id': u'mem2'}
      },
      {
        'execute': 'device_del',
        'arguments': {'id': u'dimm1'}
      },
      {
        'execute': 'object-del',
        'arguments': {'id': u'mem1'}
      },
      {'execute': 'query-memory-devices'}
    ]

    self.assertEqual(len(self.call_stack_list), 9)
    self.assertEqual(self.call_stack_list, expected_result)

  def test_updateDevice_memory_no_update(self):
    qmpwrapper = QemuQMPWrapper(self.socket_file, auto_connect=False)
    qmpwrapper._send = self.fake_send
    self.hotplugged_memory_amount = 3072
    # slot of 1G
    self.memory_slot_size = 1024
    # no changes
    cpu_option = {
      'device': 'memory',
      'nslot': 4,
      'mem': self.hotplugged_memory_amount,
      'slot': self.memory_slot_size
    }
    qmpwrapper.updateDevice(cpu_option)
    expected_result = [
      {'execute': 'query-memory-devices'},
      {'execute': 'query-memdev'}
    ]

    self.assertEqual(len(self.call_stack_list), 2)
    self.assertEqual(self.call_stack_list, expected_result)

  def test_updateDevice_memory_will_reboot(self):
    qmpwrapper = QemuQMPWrapper(self.socket_file, auto_connect=False)
    qmpwrapper._send = self.fake_send
    qmpwrapper.getEventList = self.fake_getEventList
    self.fail = True
    self.hotplugged_memory_amount = 3072
    # slot of 1G
    self.memory_slot_size = 1024
    # decrease memory to 1G, expext remove slot 3 and 2.
    cpu_option = {
      'device': 'memory',
      'nslot': 4,
      'mem': 1024,
      'slot': self.memory_slot_size,
      'canreboot': True
    }
    with self.assertRaises(QmpDeviceRemoveError):
      qmpwrapper.updateDevice(cpu_option)
    expected_result = [
      {'execute': 'query-memory-devices'},
      {'execute': 'query-memdev'},
      {
        'execute': 'device_del',
        'arguments': {'id': u'dimm3'}
      },
      {
        'execute': 'device_del',
        'arguments': {'id': u'dimm3'}
      },
      {
        'execute': 'device_del',
        'arguments': {'id': u'dimm3'}
      },
      {
        'execute': 'device_del',
        'arguments': {'id': u'dimm3'}
      },
      {
        'execute': 'device_del',
        'arguments': {'id': u'dimm3'}
      },
      {'execute': 'system_powerdown'},
      {'execute': 'quit'}
    ]

    self.assertEqual(len(self.call_stack_list), 9)
    self.assertEqual(self.call_stack_list, expected_result)

if __name__ == '__main__':
  unittest.main()

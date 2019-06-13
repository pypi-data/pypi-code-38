##############################################################################
#
# Copyright (c) 2013 Vifib SARL and Contributors. All Rights Reserved.
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

import argparse
import json
import os
import pprint
import socket
import time
import errno
import psutil
from operator import itemgetter

def parseArgument():
  """
  Very basic argument parser. Might blow up for anything else than
  "./executable mysocket.sock stop/resume".
  """
  parser = argparse.ArgumentParser()
  parser.add_argument('--suspend', action='store_const', dest='action', const='suspend')
  parser.add_argument('--resume', action='store_const', dest='action', const='resume')
  parser.add_argument('--create-snapshot', action='store_const', dest='action', const='createSnapshot')
  parser.add_argument('--create-internal-snapshot', action='store_const', dest='action', const='createInternalSnapshot')
  parser.add_argument('--delete-internal-snapshot', action='store_const', dest='action', const='deleteInternalSnapshot')
  parser.add_argument('--drive-backup', action='store_const', dest='action', const='driveBackup') 
  parser.add_argument('--query-commands', action='store_const', dest='action', const='queryCommands')
  parser.add_argument('--query-item', dest='query', choices=[
    "cpus", "hotpluggable-cpus", "memory-devices", "memdev", "balloon",
    "pci", "status", "acpi-ospm-status"])
  parser.add_argument('--update-device', action='store_const', dest='action', const='updateDevice') 
  parser.add_argument('--device-options', dest='device_options',
    help="Option used for update-device:\n" \
      '"device=cpu,amount=VALUE_INT[,model=MODEL]"\n OR '\
      '"device=memory,mem=VALUE_MB[,slot=VALUE_MB],nslot=VALUE_INT[,canreboot=0|1]"')

  parser.add_argument('--socket', dest='unix_socket_location', required=True)
  parser.add_argument('remainding_argument_list', nargs=argparse.REMAINDER)
  return  parser.parse_args()

def getInitialQemuResourceDict(pid_file):
  """
    Return CPU ad RAM initial values used to start Qemu process
  """
  if not os.path.exists(pid_file):
    return None

  with open(pid_file) as f:
    try:
      pid = int(f.read())
    except ValueError, e:
      raise ValueError("%r is empty or doesn't contain a valid pid number: %s" % (
        pid_file, str(e)))

  wait_count = 5
  while wait_count > 0:
    try:
      process = psutil.Process(pid)
      break
    except psutil.NoSuchProcess:
      print "Qemu process is not started yet..."
      wait_count -= 1
      time.sleep(0.5)
  else:
    raise ValueError('No process with pid %s' % pid)

  if not process.name().startswith('qemu-system'):
    raise ValueError("The pid %s is used by %r and not a qemu process." % (
      pid, process.name()))
  resource_dict = {'cpu': None, 'ram': None}
  cmd_list = process.cmdline()
  cpu_index = cmd_list.index('-smp')
  ram_index = cmd_list.index('-m')
  if cpu_index >= 0:
    resource_dict['cpu'] = cmd_list[cpu_index + 1].split(',')[0]
  if ram_index >= 0:
    resource_dict['ram'] = cmd_list[ram_index + 1].split(',')[0]

  return resource_dict

class QmpCommandError(Exception):
  pass

class QmpDeviceRemoveError(Exception):
  pass

class QemuQMPWrapper(object):
  """
  Small wrapper around Qemu's QMP to control a qemu VM.
  See http://git.qemu.org/?p=qemu.git;a=blob;f=qmp-commands.hx for
  QMP API definition.
  """
  def __init__(self, unix_socket_location, auto_connect=True):
    self._event_list = []
    self.socket = None
    self.sockf = None
    if auto_connect:
      self.socket = self.connectToQemu(unix_socket_location)
      self.sockf = self.socket.makefile()
      self.capabilities()

  @staticmethod
  def connectToQemu(unix_socket_location):
    """
    Create a socket, connect to qemu, be sure it answers, return socket.
    """
    if not os.path.exists(unix_socket_location):
      raise Exception('unix socket %s does not exist.' % unix_socket_location)

    print 'Connecting to qemu...'
    so = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    connected = False
    while not connected:
      try:
        so.connect(unix_socket_location)
      except socket.error:
        time.sleep(1)
        print 'Could not connect, retrying...'
      else:
        connected = True
    so.recv(1024)

    return so

  def _readResponse(self, only_event=False):
    response = None
    while True:
      data = self.sockf.readline()
      if not data:
        return
      try:
        response = json.loads(data)
      except ValueError:
        raise ValueError('Wrong data: %s' % data)
      if 'error' in response:
        raise QmpCommandError(response["error"]["desc"])
      if 'event' in response:
        self._event_list.append(response)
        print response
        if not only_event:
          continue

      return response

  def _send(self, message, retry=0, sleep=0.5):
    self.socket.sendall(json.dumps(message))
    response = self._readResponse()
    for i in range(0, retry):
      if response is not None:
        break
      print "Retrying send command after %s second(s)..." % sleep
      time.sleep(sleep)
      self.socket.sendall(json.dumps(message))
      response = self._readResponse()
    return response

  def _getVMStatus(self):
    response = self._send({'execute': 'query-status'})
    if response:
      return self._send({'execute': 'query-status'})['return']['status']
    else:
      raise IOError('Empty answer')

  def _waitForVMStatus(self, wanted_status):
    while True:
      try:
        actual_status = self._getVMStatus()
        if actual_status == wanted_status:
          return
        else:
          print 'VM in %s status, wanting it to be %s, retrying...' % (
              actual_status, wanted_status)
          time.sleep(1)
      except IOError:
          print 'VM not ready, retrying...'

  def capabilities(self):
    print 'Asking for capabilities...'
    self._send({'execute': 'qmp_capabilities'})

  def getEventList(self, timeout=0, cleanup=False):
    """
    Get a list of available QMP events.
    """

    if self.socket is None:
      return []
    if cleanup:
      self.cleanupEventList()
    if not self._event_list and timeout > 0:
      self.socket.settimeout(timeout)
      try:
        # Read then wait a bit
        self._readResponse(only_event=True)
      except socket.timeout:
        pass
      finally:
        self.socket.settimeout(None)
    else:
      self.socket.setblocking(0)
      try:
        self._readResponse(only_event=True)
      except socket.error, err:
        if err[0] == errno.EAGAIN:
          # No data available
          pass
      finally:
        self.socket.setblocking(1)

    return self._event_list

  def cleanupEventList(self):
    """
    Clear current list of pending events.
    """
    self.__events = []

  def setVNCPassword(self, password):
    # Set VNC password
    print 'Setting VNC password...'
    result = self._send({
      "execute": "change",
      "arguments": {
        "device": "vnc",
        "target": "password",
        "arg": password
      }
    })
    if result and result.get('return', None) != {}:
      raise ValueError(result)
    print 'Done.'

  def powerdown(self):
    print 'Stopping the VM...'
    self._send({'execute': 'system_powerdown'})

  def suspend(self):
    print 'Suspending VM...'
    self._send({'execute': 'stop'})
    self._waitForVMStatus('paused')

  def resume(self):
    print 'Resuming VM...'
    self._send({'execute': 'cont'})
    self._waitForVMStatus('running')

  def _queryBlockJobs(self, device):
    return self._send({'execute': 'query-block-jobs'})

  def _getRunningJobList(self, device):
    result = self._queryBlockJobs(device)
    max_loop = 20

    while max_loop and result is None:
      # If result is None retry to command until if return something.
      max_loop -= 1
      time.sleep(3)
      result = self._queryBlockJobs(device)
    if result and result.get('return'):
      return result['return']
    else:
      return

  def driveBackup(self, backup_target, source_device='virtio0', sync_type='full'):
    print 'Asking Qemu to perform backup to %s' % backup_target
    # XXX: check for error
    self._send({
        'execute': 'drive-backup',
        'arguments': {
            'device': source_device,
            'sync': sync_type,
            'target': backup_target,
         }
    })
    while self._getRunningJobList(backup_target):
      print 'Job is not finished yet.'
      time.sleep(20)

  def createSnapshot(self, snapshot_file, device='virtio0'):
    print self._send({
        'execute': 'blockdev-snapshot-sync',
        'arguments': {
            'device': device,
            'snapshot-file': snapshot_file,
         }
    })

  def createInternalSnapshot(self, name=None, device='virtio0'):
    if name is None:
      name = int(time.time())
    self._send({
        'execute': 'blockdev-snapshot-internal-sync',
        'arguments': {
            'device': device,
            'name': name,
         }
    })

  def deleteInternalSnapshot(self, name, device='virtio0'):
    self._send({
        'execute': 'blockdev-snapshot-delete-internal-sync',
        'arguments': {
            'device': device,
            'name': name,
         }
    })

  def getCPUInfo(self):
    """
      return some info about VM CPUs
    """
    cpu_info_dict = {'hotplugged': [], 'base': []}
    cpu_list = self._send({
      'execute': 'query-cpus'
    }, retry=5)['return']
    for cpu in cpu_list:
      if 'unattached' in cpu['qom_path']:
        index = 'base'
      else:
        index = 'hotplugged'
      cpu_info_dict[index].append({
        'props': cpu['props'],
        'CPU': cpu['CPU'],
        'qom_path': cpu['qom_path']
      })
    return cpu_info_dict

  def getMemoryInfo(self):
    """
      return some info about VM Memory. Can only say info about hotplugged RAM
    """
    mem_info_dict = {'hotplugged': [], 'base': []}
    memory_list = self._send({
      'execute': 'query-memory-devices'
    }, retry=5)['return']
    for mem in memory_list:
      if mem['data']['hotplugged'] == True:
        mem_info_dict['hotplugged'].append(mem['data'])

    return mem_info_dict

  def _removeDevice(self, dev_id, command_dict, auto_reboot=False):
    max_retry = 5
    result = None
    resend = True
    stop_retry = False
    while max_retry > 0:
      max_retry -= 1
      try:
        if resend:
          result = self._send(command_dict)
      except QmpCommandError, e:
        print "ERROR: ", str(e)
        print "%s\nRetry remove %r in few seconds..." % (result, dev_id)
        resend = True
      else:
        for event in self.getEventList(timeout=2, cleanup=True):
          if 'ACPI_DEVICE_OST' == event['event']:
            # request was received
            resend = False
          if 'DEVICE_DELETED' == event['event']:
            # device was deleted
            stop_retry = True
            break
        if stop_retry:
          break
        elif result is None and max_retry > 0:
          print "Retry remove %r in few seconds..." % dev_id
      time.sleep(2)

    if result is not None:
      if result.get('return', None) == {} or ('error' in result and \
          result['error'].get('class', '') == 'DeviceNotFound'):
        print 'Device %s was removed.' % dev_id
        return

    # device was not remove after retries
    if not auto_reboot:
      raise ValueError("Cannot remove device %s" % dev_id)

    # try soft reboot of the VM
    self.powerdown()
    system_exited = False
    # wait for ~10 seconds if the system exit, else quit Qemu
    for i in range(0, 5):
      for event in self.getEventList(timeout=2, cleanup=True):
        if event['event'] == 'SHUTDOWN':
          # qemu is about to exit
          system_exited = True
      if system_exited:
        break
      else:
        time.sleep(2)

    if not system_exited:
      # hard reset the VM
      print "Trying hard shutdown of the VM..."
      self._send({"execute": "quit"})

    raise QmpDeviceRemoveError("Stopped Qemu in order to remove the device %r" % dev_id)


  def _updateCPU(self, amount, cpu_model):
    """
      Add or remove CPU according current value
      amount: number of CPU to update to
    """
    cpu_amount = 0
    empty_socket_list = []
    used_socket_id_list = []
    unremovable_cpu = 0
    cpu_hotplugable_list = self._send({
      'execute': 'query-hotpluggable-cpus'
    }, retry=5)['return']
    cpu_hotplugable_list.reverse()
    for cpu in cpu_hotplugable_list:
      if cpu.get('qom-path', '') == '':
        if len(empty_socket_list) < amount:
          cpu['props']['driver'] = cpu_model
          cpu['props']['id'] = 'cpu%s' % (cpu['props']['socket-id'])
          empty_socket_list.append(cpu['props'])
      else:
        # if this is an hotpluggable cpu
        if '/machine/peripheral' in cpu.get('qom-path', ''):
          used_socket_id_list.append('cpu%s' % (cpu['props']['socket-id']))
          cpu_amount += 1
        else:
          unremovable_cpu += 1

    hotplug_amount = amount - unremovable_cpu # get only hotpluggable CPU
    if hotplug_amount < 0:
      raise ValueError("Unattached CPU amount is %s, cannot update to %s" % (
        unremovable_cpu, amount))
    cpu_diff = hotplug_amount - cpu_amount
    max_hotplug_cpu = len(empty_socket_list)

    if cpu_amount == hotplug_amount:
      # no chanches
      print "Hotplug CPU is up to date."
      return

    if cpu_amount > hotplug_amount:
      # we will remove CPU
      cpu_diff = -1 * cpu_diff
      if cpu_diff >= 1:
        print "Request remove %s CPUs..." % cpu_diff
        used_socket_id_list.reverse()
        for i in range(0, cpu_diff):
          self._removeDevice(used_socket_id_list[i], {
            'execute': 'device_del',
            'arguments': {'id': used_socket_id_list[i]}
          })
    elif cpu_amount < hotplug_amount:
      if max_hotplug_cpu < cpu_diff:
        # no hotplugable cpu socket found for Add
        raise ValueError("Cannot Configure %s CPUs, the maximum amount of " \
          "hotplugable CPU is %s!" % (hotplug_amount, max_hotplug_cpu))
      print "Adding %s CPUs..." % cpu_diff 
      for i in range(0, cpu_diff):
        self._send({
            'execute': 'device_add',
            'arguments': empty_socket_list[i]
        })

    # check that hotplugged memery amount is consistent
    cpu_info = self.getCPUInfo()
    final_cpu_count = len(cpu_info['hotplugged'])
    if hotplug_amount != final_cpu_count:
      raise ValueError("Consistency error: Expected %s hotplugged CPU(s) but" \
        " current CPU amount is %s" % (hotplug_amount, final_cpu_count))
    print "Done."

  def _removeMemory(self, id_dict, auto_reboot=False):
    print "Trying to remove devices %s, %s..." % (id_dict['id'], id_dict['memdev'])
    self._removeDevice(id_dict['id'] ,{
      'execute': 'device_del',
      'arguments': {'id': id_dict['id']}
    }, auto_reboot=auto_reboot)
    # when dimm is removed, remove memdev object
    self._removeDevice(id_dict['memdev'], {
      'execute': 'object-del',
      'arguments': {
        'id': id_dict['memdev']
      }
    }, auto_reboot=auto_reboot)

  def _updateMemory(self, mem_size, slot_size, slot_amount, allow_reboot=False):
    """
      Update memory size according to the current value. option_dict contains:

      slot_amount: amount of slots available
      mem_size: Size of memory to allocate
      slot_size: size of the memory per slot (this value should not change).
        default: 512 MB

      ex: to add 2G of RAM, mem=2048,slot=512 => allocate 4 slots
          to reduce to 1G of RAM, mem=1024,slot=512 => allocate 2 slots
    """

    current_size = 0
    num_slot_used = 0
    memory_id_list = [] # current hotplugged memory
    cleanup_memdev_id_dict = {}
    current_dimm_list = self._send({ "execute": "query-memory-devices" }, retry=5)
    current_memdev_list = self._send({ "execute": "query-memdev" }, retry=5)

    for memdev in current_memdev_list['return']:
      cleanup_memdev_id_dict[memdev['id']] = ''

    for dimm in current_dimm_list['return']:
      current_size += dimm['data']['size']
      if dimm['data']['hotplugged']:
        mem_dev = os.path.basename(dimm['data']['memdev'])
        cleanup_memdev_id_dict.pop(mem_dev)
        memory_id_list.append({
        'memdev': mem_dev,
         'id': dimm['data']['id'],
         'size': dimm['data']['size']/(1024 * 1024),
       })
    memory_id_list = sorted(memory_id_list, key=itemgetter('id'))

    # cleanup memdev that was not removed because of failure
    for memdev in cleanup_memdev_id_dict.keys():
      print "Cleaning up memdev %s..." % memdev
      self._removeDevice(memdev, {
        'execute': 'object-del',
        'arguments': {
          'id': memdev
        }
      }, auto_reboot=allow_reboot)

    num_slot_used = len(memory_id_list)
    if (mem_size % slot_size) != 0:
      raise ValueError("Memory size %r is not a multiple of %r" % (mem_size,
        slot_size))
    if (mem_size / slot_size) > slot_amount:
      raise ValueError("No enough slots available to add %sMB of RAM" % mem_size)

    current_size = current_size/(1024 * 1024)
    if current_size == mem_size:
      print "Hotplug Memory size is up to date."
      return

    if mem_size < 0:
      raise ValueError("Memory size is not valid: %s" % option_dict)
    elif current_size > mem_size:
      # Request to remove memory
      to_remove_size = current_size - mem_size
      print "Removing %s MB of memory..." % to_remove_size

      for i in range(num_slot_used, 0, -1):
        # remove all slots that won't be used
        index = i - 1
        to_remove_size -= memory_id_list[index]['size']
        if to_remove_size >= 0:
          self._removeMemory(memory_id_list[index], auto_reboot=allow_reboot)
          if to_remove_size == 0:
            break
        else:
          raise ValueError("Cannot remove the requested size of memory. " \
            "Remaining to remove: %s, RAM slot size: %s" % (
              to_remove_size + memory_id_list[index]['size'],
              memory_id_list[index]['size'])
            )
    elif current_size < mem_size:
      # ask for increase memory
      slot_add = (mem_size - current_size) / slot_size

      print "Adding %s memory slot(s) of %s MB..." % (slot_add, slot_size)
      for i in range(0, slot_add):
        index = num_slot_used + i + 1
        self._send({
            'execute': 'object-add',
            'arguments': {
              'qom-type': 'memory-backend-ram',
              'id': 'mem%s' % index,
              'props': { 'size': slot_size * 1024 * 1024 }
            }
        })
        self._send({
            'execute': 'device_add',
            'arguments': {
              'driver': 'pc-dimm' ,
              'id': 'dimm%s' % index,
              'memdev': 'mem%s' % index
            }
          })

    # check that hotplugged memery amount is consistent
    mem_info = self.getMemoryInfo()
    final_mem_size = 0
    for mem in mem_info['hotplugged']:
      final_mem_size += mem['size']
    final_mem_size = final_mem_size / (1024 * 1024) # get size in MB
    if mem_size != final_mem_size:
      raise ValueError("Consistency error: Expected %s MB of hotplugged RAM " \
        "but current RAM size is %s MB" % (mem_size, final_mem_size))
    print "Done."

  def updateDevice(self, option_dict):
    argument_dict = {}
    if option_dict.has_key('device'):
      if option_dict['device'] == 'cpu':
        return self._updateCPU(
          amount=int(option_dict['amount']),
          cpu_model=option_dict.get('model', 'qemu64-x86_64-cpu')
        )
      elif option_dict['device'] == 'memory':
        return self._updateMemory(
          mem_size=int(option_dict['mem']),
          slot_size=int(option_dict['slot']),
          slot_amount=int(option_dict['nslot']),
          allow_reboot=int(option_dict.get('canreboot', 0)) in [1, True]
        )
      else:
        raise ValueError("Unknown device type: %s" % option_dict)
    else:
      raise ValueError("Options are unknown: %s" % option_dict)

  def queryCommands(self, query=None):
    if query is not None:
      pprint.pprint(self._send({'execute': 'query-%s' % query})['return'])
    else:
      pprint.pprint(self._send({'execute': 'query-commands'})['return'])

def main():
  config = parseArgument()
  qemu_wrapper = QemuQMPWrapper(config.unix_socket_location)

  if config.remainding_argument_list:
    getattr(qemu_wrapper, config.action)(*config.remainding_argument_list)
  else:
    if config.query != None:
      getattr(qemu_wrapper, config.action)(**{"query": config.query})
    elif config.action =="updateDevice":
      argument_dict = {}
      for parameter in config.device_options.split(','):
        parameter_list = parameter.split('=')
        argument_dict[parameter_list[0].strip()] = parameter_list[1].strip()
      getattr(qemu_wrapper, config.action)(argument_dict)
    else:
      getattr(qemu_wrapper, config.action)()

if __name__ == '__main__':
  main()


# Copyright 2018 CERN
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
collectd sensor for puppet's last_run_summary.yaml file.

To configure with collectd

<Plugin "python">
  LogTraces true
  Interactive false
  Import "collectd_puppet"
  <Module "collectd_puppet">
    path "/opt/puppetlabs/puppet/cache/state/last_run_summary.yaml"
    MaxRetention 21600
  </Module>
</Plugin>
"""

import os
import time
import collectd
import yaml

PATH = "/opt/puppetlabs/puppet/cache/state/last_run_summary.yaml"
STATE = "/var/lib/collectd/puppet.state"
MAX_RETENTION = 60*60*6

META = {'schema_version': 2}

def config_func(config):
    """ accept configuration from collectd """
    path_set = False
    for node in config.children:
        key = node.key.lower()
        val = node.values[0]
        if key == 'path':
            global PATH
            PATH = val
            path_set = True
        if key == 'maxretention':
            global MAX_RETENTION
            MAX_RETENTION = val
            collectd.info('puppet plugin: Using overridden MaxRetention %s' % MAX_RETENTION)
        else:
            collectd.info('puppet plugin: Unknown config key "%s"' % key)

    if path_set:
        collectd.info('puppet plugin: Using overridden path %s' % PATH)
    else:
        collectd.info('puppet plugin: Using default path %s' % PATH)

def read_func():
    """ open yaml file and publish if Puppet has run """
    try:
        last_polled = os.stat(STATE).st_mtime
    except OSError:
        last_polled = 0
    last_puppet_run = os.stat(PATH).st_mtime

    if last_polled >= last_puppet_run:
        return

    with open(PATH, 'r') as stream:
        try:
            data = yaml.load(stream)
            with open(STATE, 'a'):
                os.utime(STATE, None)
        except yaml.YAMLError as exc:
            print(exc)

    # This group of values is always populated, even on a compilation error
    sources = [
        ('last_run', 'time_ref', data['time']['last_run']),
        ('compiled', 'boolean', 1 if 'config_retrieval' in data['time'] else 0),
    ]

    # This group of values is only populated when the compilation is successful
    # (the catalog has resources)
    if 'resources' in data and data['resources']['total'] > 0:
        sources.extend([
            ('total', 'resources', data['resources']['total']),
            ('changed', 'resources', data['resources']['changed']),
            ('corrective_change', 'resources', data['resources']['corrective_change']),
            ('failed', 'resources', data['resources']['failed']),
            ('failed_to_restart', 'resources', data['resources']['failed_to_restart']),
            ('out_of_sync', 'resources', data['resources']['out_of_sync']),
            ('restarted', 'resources', data['resources']['restarted']),
            ('scheduled', 'resources', data['resources']['scheduled']),
            ('skipped', 'resources', data['resources']['skipped']),
            ('total_time', 'seconds', data['time']['total']),
            ('config_retrieval', 'seconds', data['time']['config_retrieval']),
        ])

    for type_instance, _type, value in sources:
        collectd.Values(plugin='puppet',
                        type=_type,
                        type_instance=type_instance,
                        meta=META).dispatch(values=[value], interval=MAX_RETENTION)

collectd.register_config(config_func)
collectd.register_read(read_func)

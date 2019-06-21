#
#    ICRAR - International Centre for Radio Astronomy Research
#    (c) UWA - The University of Western Australia, 2018
#    Copyright by UWA (in the framework of the ICRAR)
#    All rights reserved
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston,
#    MA 02111-1307  USA
#

import collections
import logging

import boto3


logger = logging.getLogger(__name__)

def _start_instances(instances, *args, **kwargs):

    # group instances by type and create them
    unique = set(instances)
    per_type = {instances.count(u): u for u in unique}
    session = boto3.Session(*args, **kwargs)
    ec2 = session.resource('ec2')

    actual_instances = []
    for count, typ in per_type.items():
        actual_instances.extend(ec2.create_instances(InstanceType=typ, ImageId='ami-d3daace9', MinCount=count, MaxCount=count))
    return actual_instances

instance_info = collections.namedtuple('instance_info', 'cpu mem')
instance_priced_info = collections.namedtuple('instance_priced_info', 'cpu credits_hr mem')

_resources = {

    # t3 instances
    instance_priced_info(2, 6, 0.5): 't3.nano',
    instance_priced_info(2, 12, 1): 't3.micro',
    instance_priced_info(2, 24, 2): 't3.small',
    instance_priced_info(2, 12, 1): 't3.micro',
    instance_priced_info(2, 24, 4): 't3.medium',
    instance_priced_info(2, 36, 8): 't3.large',
    instance_priced_info(4, 96, 16): 't3.xlarge',
    instance_priced_info(8, 192, 32): 't3.2xlarge',

    # t2 instances
    instance_priced_info(1, 3, 0.5): 't2.nano',
    instance_priced_info(1, 6, 1): 't2.micro',
    instance_priced_info(1, 12, 2): 't2.small',
    instance_priced_info(2, 24, 4): 't2.medium',
    instance_priced_info(2, 36, 8): 't2.large',
    instance_priced_info(4, 54, 16): 't2.xlarge',
    instance_priced_info(8, 81, 32): 't2.2xlarge',

    # m5 instances
    instance_info(2, 8): 'm5.large',
    instance_info(4, 16): 'm5.xlarge',
    instance_info(8, 32): 'm5.2xlarge',
    instance_info(16, 64): 'm5.4xlarge',
    instance_info(48, 192): 'm5.12xlarge',
    instance_info(96, 384): 'm5.24xlarge',
    instance_info(2, 8): 'm5d.large',
    instance_info(4, 16): 'm5d.xlarge',
    instance_info(8, 32): 'm5d.2xlarge',
    instance_info(16, 64): 'm5d.4xlarge ',
    instance_info(48, 192): 'm5d.12xlarge',
    instance_info(96, 384): 'm5d.24xlarge',

    # m4 instances
    instance_info(2, 8): 'm4.large',
    instance_info(4, 16): 'm4.xlarge',
    instance_info(8, 32): 'm4.2xlarge',
    instance_info(16, 64): 'm4.4xlarge',
    instance_info(40, 160): 'm4.10xlarge',
    instance_info(64, 256): 'm4.16xlarge',
}

def _best_fit(cpu, mem):

    # Find all instances that have the minimum required number of CPUs
    while True:

        # instances with at least 'cpu' CPUs. If none, there is no possible fit
        cpu_bound = list(filter(lambda c: c >= cpu, [r.cpu for r in _resources]))
        if not cpu_bound:
            return []

        # instances with the minimum required number of CPUs and at least
        # the required amount of memory
        cpu_bound = list(filter(lambda x: x.cpu == min(cpu_bound), _resources))
        mem_bound = list(filter(lambda m: m >= mem, [r.mem for r in cpu_bound]))
        if mem_bound:
            break

        # Nothing found, let's try with more CPUs
        cpu += 1

    mem_bound_instances = list(filter(lambda x: x.mem == min(mem_bound), cpu_bound))
    return mem_bound_instances[0]

def _iterable(x):
    try:
        iter(x)
        return x
    except AttributeError:
        return x,

def start(cpu_reqs, memory_reqs, *args, **kwargs):

    cpu_reqs = _iterable(cpu_reqs)
    memory_reqs = _iterable(memory_reqs)
    if len(cpu_reqs) != len(cpu_reqs):
        raise ValueError("#cpu requirements != #memory requirements")

    instances = [_best_fit(c, m) for c, m in zip(cpu_reqs, memory_reqs)]

    logger.info("Best fit for requirements cpus=%r, mem=%r are: %r. Starting them now")

    instances = _start_instances([_resources[i] for i in instances], *args, **kwargs)
    logger.info("Instances started, waiting for them to come up")

if __name__ == '__main__':
    instances = start([1, 1], [2, 2], profile_name='rtobar@icrar-sdp-aws')
    print(instances)
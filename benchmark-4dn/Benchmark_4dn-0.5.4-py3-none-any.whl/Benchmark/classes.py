import os
import csv
import re
from Benchmark.byteformat import MB2GB


class BenchmarkResult(object):
    def __init__(self, size, mem, cpu, exclude_a1=True, exclude_t=False):
        self.total_size_in_GB = size
        self.total_mem_in_MB = mem
        self.min_CPU = cpu
        self.aws = get_optimal_instance_type(cpu=cpu,
                                             mem_in_gb=MB2GB(mem),
                                             exclude_a1=exclude_a1, exclude_t=exclude_t)

    def as_dict(self):
        return rdict(self)


class OptimalInstance(object):
    def __init__(self, cost_in_usd, mem_in_gb=None, cpu=None,
                 recommended_instance_type=None, EBS_optimized=None,
                 EBS_optimization_surcharge=None):
        self.cost_in_usd = cost_in_usd
        self.mem_in_gb = mem_in_gb
        self.cpu = cpu
        self.recommended_instance_type = recommended_instance_type
        self.EBS_optimized = EBS_optimized
        self.EBS_optimization_surcharge = EBS_optimization_surcharge

    def reset(self, cost_in_usd=None, mem_in_gb=None, cpu=None,
              recommended_instance_type=None, EBS_optimized=None,
              EBS_optimization_surcharge=None):
        if cost_in_usd:
            self.cost_in_usd = cost_in_usd
        if mem_in_gb:
            self.mem_in_gb = mem_in_gb
        if cpu:
            self.cpu = cpu
        if recommended_instance_type:
            self.recommended_instance_type = recommended_instance_type
        if EBS_optimized is not None:
            self.EBS_optimized = EBS_optimized
        if EBS_optimization_surcharge:
            self.EBS_optimization_surcharge = EBS_optimization_surcharge

    def as_dict(self):
        return rdict(self)


def rdict(x):
    """
    recursive conversion to dictionary
    converts objects in list members to dictionary recursively
    """
    if isinstance(x, list):
        l = [rdict(_) for _ in x]
        return l
    elif isinstance(x, dict):
        x2 = {}
        for k, v in x.items():
            x2[k] = rdict(v)
        return x2
    else:
        if hasattr(x, '__dict__'):
            d = x.__dict__
            toremove = []
            for k, v in d.items():
                if v is None:
                    toremove.append(k)
                else:
                    d[k] = rdict(v)
            for k in toremove:
                del(d[k])
            return d
        else:
            return x


def get_aws_ec2_info_file():
    this_dir, _ = os.path.split(__file__)
    return(os.path.join(this_dir, "aws", "Amazon EC2 Instance Comparison.csv"))


def get_optimal_instance_type(cpu=1, mem_in_gb=0.5,
                              instance_info_file=get_aws_ec2_info_file(),
                              exclude_a1=True, exclude_t=False):
    res = OptimalInstance(100000)
    with open(instance_info_file, "r") as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in spamreader:
            row_instance_type = row['API Name']
            if exclude_a1 and row_instance_type.startswith('a1'):  # skip a1 instances
                continue
            if exclude_t and row_instance_type.startswith('t'):  # skip t instances
                continue
            row_cost_str = row['Linux On Demand cost']
            if row_cost_str == 'unavailable':
                continue
            row_cost = float(row_cost_str.replace(' hourly', '')
                                         .replace('$', ''))
            row_cpu = int(re.sub(" vCPUs.*", '', row['vCPUs']))
            row_mem = float(row['Memory'].replace(' GiB', ''))
            row_ebs_opt_surcharge = row['EBS Optimized surcharge']
            if row_ebs_opt_surcharge == 'unavailable':
                row_ebs_opt = False
                row_ebs_opt_surcharge = None
            else:
                row_ebs_opt = True
                row_ebs_opt_surcharge \
                    = float(row_ebs_opt_surcharge.replace(' hourly', '')
                                                 .replace('$', ''))
            if row_cpu >= cpu and row_mem >= mem_in_gb:
                if row_cost < res.cost_in_usd:
                    res.reset(row_cost, row_mem, row_cpu, row_instance_type,
                              row_ebs_opt, row_ebs_opt_surcharge)
    if res.cost_in_usd == 100000:
        raise NoMatchingInstanceException

    return(res.as_dict())


def instance_list(instance_info_file=get_aws_ec2_info_file(),
                  exclude_a1=True,
                  exclude_t=False):
    """Return all instances in the input document as list of dictionaries."""
    instances = []
    with open(instance_info_file, "r") as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in spamreader:
            row_instance_type = row['API Name']
            if exclude_a1 and row_instance_type.startswith('a1'):  # skip a1 instances
                continue
            if exclude_t and row_instance_type.startswith('t'):  # skip t instances
                continue
            row_cost_str = row['Linux On Demand cost']
            if row_cost_str == 'unavailable':
                continue
            row_cost = float(row_cost_str.replace(' hourly', '')
                                         .replace('$', ''))
            row_cpu = int(re.sub(" vCPUs.*", '', row['vCPUs']))
            row_mem = float(row['Memory'].replace(' GiB', ''))
            row_ebs_opt_surcharge = row['EBS Optimized surcharge']
            if row_ebs_opt_surcharge == 'unavailable':
                row_ebs_opt = False
                row_ebs_opt_surcharge = None
            else:
                row_ebs_opt = True
                row_ebs_opt_surcharge \
                    = float(row_ebs_opt_surcharge.replace(' hourly', '')
                                                 .replace('$', ''))
            instances.append({'cost_in_usd': row_cost,
                              'mem_in_gb': row_mem,
                              'cpu': row_cpu,
                              'instance_type': row_instance_type,
                              'EBS_optimized': row_ebs_opt,
                              'EBS_optimization_surcharge': row_ebs_opt_surcharge})
    return instances


def get_instance_types(cpu=1, mem_in_gb=0.5, instances=instance_list(), top=10, rank='cost_in_usd'):
    """Return a filtered list of instance based on cpu and memory."""
    # check that rank is a float field
    try:
        assert rank in ['cost_in_usd', 'mem_in_gb', 'cpu']
    except AssertionError:
        print('Can not order instances by {}'.format(rank))
    # filter results
    results = [i for i in instances if i['cpu'] >= cpu and i['mem_in_gb'] >= mem_in_gb]
    # order results
    results = sorted(results, key=lambda k: k[rank])
    return results[:top]


# Exceptions
class NoMatchingInstanceException(Exception):
    def __init__(self, value=None):
        if not value:
            self.value = "No EC2 instance can match the requirement."

import abc
import decimal
from datetime import datetime, timedelta

from dateutil.tz import tzutc

from spell.cli.utils import prettify_timespan

# hyperparameter scaling constants
LINEAR = "linear"
LOG = "log"
REVERSE_LOG = "reverse_log"

# hyperparameter type constants
FLOAT = "float"
INT = "int"


class Model(object):
    __metaclass__ = abc.ABCMeta

    compare_fields = abc.abstractproperty()

    def __eq__(self, other):
        if not hasattr(other, "__dict__"):
            return False
        my_items = filter(lambda x: x[0] in self.compare_fields, self.__dict__.items())
        other_items = filter(lambda x: x[0] in self.compare_fields, other.__dict__.items())
        return set(my_items) == set(other_items)

    def __hash__(self):
        my_items = filter(lambda x: x[0] in self.compare_fields, self.__dict__.items())
        return hash(tuple(sorted(my_items)))

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, ", ".join(
                               ["{}={}".format(x, repr(y)) for x, y in self.__dict__.items() if y]))


class User(Model):

    compare_fields = ["email", "user_name", "full_name", "created_at"]

    def __init__(self, email, user_name, created_at, updated_at,
                 full_name=None, last_logged_in=None, **kwargs):
        self.email = email
        self.user_name = user_name
        self.full_name = full_name
        self.created_at = created_at
        self.updated_at = updated_at
        self.last_logged_in = last_logged_in
        self.memberships = kwargs.get("memberships")


class Organization(Model):

    compare_fields = ["name", "created_at"]

    def __init__(self, **kwargs):
        self.name = kwargs["name"]
        self.members = kwargs.get("members", [])
        self.created_at = kwargs["created_at"]
        self.updated_at = kwargs["updated_at"]


class Owner(Model):

    compare_fields = ["name", "type"]

    def __init__(self, name, type, **kwargs):
        self.name = name
        self.type = type
        self.requestor_role = kwargs.get("requestor_role")
        self.permissions = kwargs.get("permissions")
        self.github_username = kwargs.get("github_username")
        self.clusters = kwargs.get("clusters")


class OrgMember(Model):

    compare_fields = ["organization", "user", "role", "created_at"]

    def __init__(self, **kwargs):
        self.organization = kwargs.get("organization")
        self.user = kwargs.get("user")
        self.role = kwargs["role"]
        self.created_at = kwargs["created_at"]
        self.updated_at = kwargs["updated_at"]


class Key(Model):

    compare_fields = ["id", "title", "fingerprint", "created_at"]

    def __init__(self, id, title, fingerprint, verified, created_at, **kwargs):
        self.id = int(id)
        self.title = title
        self.fingerprint = fingerprint
        self.verified = verified
        self.created_at = created_at


class Workspace(Model):

    compare_fields = ["id", "root_commit", "name", "description", "git_remote_url", "creator", "created_at"]

    def __init__(self, id, root_commit, name, description, git_remote_url, creator, created_at, updated_at,
                 git_commit_hash=None, **kwargs):
        self.id = int(id)
        self.root_commit = root_commit
        self.name = name
        self.description = description
        self.git_remote_url = git_remote_url
        self.creator = creator
        self.created_at = created_at
        self.updated_at = updated_at
        self.git_commit_hash = git_commit_hash


class Run(Model):

    compare_fields = ["id", "status", "command", "creator", "gpu", "git_commit_hash", "docker_image", "framework",
                      "workspace", "pip_packages", "apt_packages", "attached_resources", "environment_vars",
                      "distributed"]

    def __init__(self, id, status, command, creator, gpu, git_commit_hash, description, framework, docker_image,
                 created_at, workspace=None, pip_packages=None, apt_packages=None, attached_resources=None,
                 environment_vars=None, user_exit_code=None, started_at=None, ended_at=None, hyper_params=None,
                 github_url=None, distributed=None, **kwargs):
        self.id = int(id)
        self.status = status
        self.user_exit_code = user_exit_code if user_exit_code is None else int(user_exit_code)
        self.command = command
        self.creator = creator
        self.gpu = gpu
        self.git_commit_hash = git_commit_hash
        self.github_url = github_url
        self.description = description
        self.distributed = distributed
        self.docker_image = docker_image
        self.framework = framework
        self.created_at = created_at
        self.started_at = started_at
        self.ended_at = ended_at
        self.workspace = workspace
        self.pip_packages = pip_packages or []
        self.apt_packages = apt_packages or []
        self.attached_resources = attached_resources or {}
        self.environment_vars = environment_vars or {}
        self.already_existed = False
        self.hyper_params = hyper_params


class HyperSearch(Model):

    compare_fields = ["id", "runs"]

    def __init__(self, id, runs=None, **kwargs):
        self.id = int(id)
        self.runs = runs or []


class Workflow(Model):

    compare_fields = ["id", "workspace_specs", "github_specs", "run"]

    def __init__(self, id, workspace_specs=None, github_specs=None, managing_run=None, runs=None, **kwargs):
        self.id = int(id)
        self.workspace_specs = workspace_specs or {}
        self.github_specs = github_specs or {}
        self.managing_run = managing_run
        self.runs = runs or[]


class LsLine(Model):

    compare_fields = ["path", "size"]

    def __init__(self, path, size, date=None, additional_info=None, link_target=None, **kwargs):
        self.path = path
        self.size = size
        self.date = date
        self.additional_info = additional_info
        self.link_target = link_target


class LogEntry(Model):

    compare_fields = ["status", "log", "status_event", "level", "timestamp"]

    def __init__(self, status=None, log=None, status_event=None, level=None, **kwargs):
        self.status = status
        self.log = log
        self.status_event = status_event
        self.level = level
        self.timestamp = kwargs.get("@timestamp")

    def __str__(self):
        return self.log


class CPUStats(Model):

    compare_fields = ["cpu_percentage", "memory", "memory_total", "memory_percentage",
                      "network_rx", "network_tx", "block_read", "block_write"]

    def __init__(self, cpu_percentage, memory, memory_total, memory_percentage,
                 network_rx, network_tx, block_read, block_write, **kwargs):
        self.cpu_percentage = cpu_percentage
        self.memory = memory
        self.memory_total = memory_total
        self.memory_percentage = memory_percentage
        self.network_rx = network_rx
        self.network_tx = network_tx
        self.block_read = block_read
        self.block_write = block_write


class GPUStats(Model):

    compare_fields = ["name", "temperature", "power_draw", "power_limit",
                      "gpu_utilization", "memory_utilization", "memory_used", "memory_total", "perf_state"]

    def __init__(self, name, temperature, power_draw, power_limit,
                 gpu_utilization, memory_utilization, memory_used, memory_total, perf_state, **kwargs):
        self.name = name
        self.temperature = temperature
        self.power_draw = power_draw
        self.power_limit = power_limit
        self.gpu_utilization = gpu_utilization
        self.memory_utilization = memory_utilization
        self.memory_used = memory_used
        self.memory_total = memory_total
        self.perf_state = perf_state


class UserDataset(Model):

    compare_fields = ["id", "name", "status", "created_at"]

    def __init__(self, id, name, status, updated_at, created_at, **kwargs):
        self.id = id
        self.name = name
        self.status = status
        self.updated_at = updated_at
        self.created_at = created_at


class Template(Model):

    compare_fields = ["body"]

    def __init__(self, body, **kwargs):
        self.body = body


class Error(Model):

    compare_fields = ["status", "error", "code"]

    def __init__(self, status, error, code):
        self.status = status
        self.error = error
        self.code = code

    @staticmethod
    def response_dict_to_object(obj):
        if "status" in obj or "error" in obj or "code" in obj:
            status = obj.get("status", None)
            error = obj.get("error", None)
            code = obj.get("code", None)
            return Error(status, error, code)
        return obj

    def __str__(self):
        if self.error:
            return self.error
        elif self.status:
            return self.status
        else:
            return None


class MachineStats(Model):
    compare_fields = ["machine_type_name", "total", "user_stats", "cost_cents_per_hour"]

    def __init__(self, machine_type_name, total, user_stats, cost_cents_per_hour):
        self.total = Stats(**total)
        self.user_stats = {name: Stats(**s) for name, s in user_stats.items()}
        self.machine_type_name = machine_type_name
        self.cost_cents_per_hour = cost_cents_per_hour


class Stats(Model):
    compare_fields = ["time_used", "cost_used_cents"]

    def __init__(self, time_used, cost_used_cents):
        self.time_used = timedelta(seconds=time_used)
        self.cost_used_usd = decimal.Decimal(cost_used_cents)/100


def parseNullDate(dt):
    if dt is None:
        return None
    return dt.date()


class BillingStatus(Model):
    compare_fields = ["plan_id", "plan_name", "remaining_credits_usd", "period_machine_stats", "total_machine_stats",
                      "last_machine_invoice_date", "next_machine_invoice_date", "total_runs", "concurrent_queued_runs",
                      "concurrent_run_limit", "previous_stripe_billing_date", "next_stripe_billing_date",
                      "used_credit_usd"]

    def __init__(self, plan_id, plan_name, remaining_credit_cents, last_machine_invoice_date,
                 period_machine_stats, total_machine_stats, concurrent_queued_runs,
                 concurrent_run_limit, total_runs, next_machine_invoice_date, previous_stripe_billing_date,
                 next_stripe_billing_date, used_credit_cents, machine_charge_cents, total_charge_cents, **kwargs):
        self.plan_id = plan_id
        self.plan_name = plan_name
        self.remaining_credits_usd = decimal.Decimal(remaining_credit_cents)/100
        self.used_credits_usd = decimal.Decimal(used_credit_cents)/100
        self.period_machine_stats = [MachineStats(**s) for s in period_machine_stats]
        self.total_machine_stats = [MachineStats(**s) for s in total_machine_stats]
        self.last_machine_invoice_date = parseNullDate(last_machine_invoice_date)
        self.next_machine_invoice_date = parseNullDate(next_machine_invoice_date)
        self.previous_stripe_billing_date = parseNullDate(previous_stripe_billing_date)
        self.next_stripe_billing_date = parseNullDate(next_stripe_billing_date)

        self.total_charge_usd = decimal.Decimal(total_charge_cents)/100
        self.machine_charge_usd = decimal.Decimal(machine_charge_cents)/100

        self.total_runs = total_runs
        self.concurrent_queued_runs = concurrent_queued_runs
        self.concurrent_run_limit = concurrent_run_limit


class ModelServer(Model):
    compare_fields = ["id", "name", "tag", "type", "resource_path", "state", "created_at",
                      "updated_at", "urls", "auth_token"]

    def __init__(self, id, server_name, tag, type, resource_path, status, url, created_at, updated_at,
                 access_token, cluster=None, **kwargs):
        self.id = id
        self.server_name = server_name
        self.tag = tag
        self.type = type
        self.resource_path = resource_path
        self.status = status
        self.url = url
        self.cluster = cluster
        self.created_at = created_at
        self.updated_at = updated_at
        self.access_token = access_token

    def get_full_name(self):
        return "{}:{}".format(self.server_name, self.tag)

    def get_age(self):
        if self.status != "running":
            return "--"
        return prettify_timespan(self.updated_at, datetime.now(tzutc()))


class ModelServerLogEntry(Model):

    compare_fields = ["log"]

    def __init__(self, log=None, **kwargs):
        self.log = log

    def __str__(self):
        return self.log


class NameVersionPair(Model):

    compare_fields = ["name", "version"]

    def __init__(self, name, version=None, **kwargs):
        self.name = name
        self.version = version

    def to_payload(self):
        return {
            "name": self.name,
            "version": self.version,
        }


class Environment(Model):

    compare_fields = ["python_2", "framework", "apt", "pip", "env_vars", "docker_image", "conda_file"]

    def __init__(self, python_2=None, framework=None, apt=None, pip=None, env_vars=None, docker_image=None,
                 conda_file=None, **kwargs):
        self.python_2 = python_2
        self.framework = NameVersionPair(**framework) if framework else None
        self.apt = [NameVersionPair(**package) for package in apt] if apt else None
        self.pip = [NameVersionPair(**package) for package in pip] if pip else None
        self.env_vars = env_vars
        self.docker_image = docker_image
        self.conda_file = conda_file

    def to_payload(self):
        return {
            "python_2": self.python_2,
            "framework": self.framework,
            "apt": self.apt,
            "pip": self.pip,
            "env_vars": self.env_vars,
            "docker_image": self.docker_image,
            "conda_env_file": self.conda_file,
        }


class RunRequest:
    """
    A class used to encapsulate all of the specifications of a Run

    Keyword arguments:
    machine_type -- which machine_type to use for the actual run
    command -- the command to run on this workspaces
    workspace_id -- the id of the workspace for this repo
    commit_hash -- the current commit hash on the repo to run
    commit_label -- the commit label for the workspace/commit hash, if the run is associated with a workflow
    cwd -- the current working directory that the user ran this cmd in
    root_directory -- the name of the top level directory for the git repository
    pip_packages -- list of pip dependencies to install
    apt_packages -- list of apt dependencies to install
    docker_image -- name of docker image to use as base
    framework -- Spell framework to use for the run, must be specified if docker_image not given
    framework_version -- Version of Spell framework to use for the run
    python2 -- a boolean indicating whether python version should be set to python 2
    attached_resources -- ids and mount points of runs to attach
    description -- a human readable description of this run
    envvars -- environment variables to set
    conda_file -- contents of conda environment.yml
    run_type -- type of run
    idempotent -- should we use an existing identical run
    provider -- if specified only machines from that provider will be used, e.g. aws
    local_root -- Used for jupyter runs
    workflow_id -- ID of the workflow to associate this run to
    github_url -- the url of a GitHub repository
    github_ref -- commit hash, branch, or tag of the repository to pull
    distributed -- the number of machines to create for the distributed run
    """
    def __init__(self, machine_type="CPU", command=None, workspace_id=None, commit_hash=None, commit_label=None,
                 cwd=None, root_directory=None, pip_packages=None, apt_packages=None, docker_image=None, framework=None,
                 framework_version=None, python2=None, attached_resources=None, description=None,
                 envvars=None, conda_file=None, run_type="user",
                 idempotent=False, provider=None, local_root=None, workflow_id=None,
                 github_url=None, github_ref=None, distributed=None):
        self.machine_type = machine_type
        self.command = command
        self.workspace_id = workspace_id
        self.commit_hash = commit_hash
        self.commit_label = commit_label
        self.cwd = cwd
        self.root_directory = root_directory
        self.pip_packages = pip_packages
        self.apt_packages = apt_packages
        self.docker_image = docker_image
        self.framework = framework
        self.framework_version = framework_version
        self.python2 = python2
        self.description = description
        self.envvars = envvars
        self.attached_resources = {name: {"mount_point": attached_resources[name]}
                                   for name in attached_resources} if attached_resources else None
        self.conda_file = conda_file
        self.run_type = run_type
        self.idempotent = idempotent
        self.provider = provider
        self.local_root = local_root
        self.workflow_id = workflow_id
        self.github_url = github_url
        self.github_ref = github_ref
        self.distributed = distributed

    def to_payload(self):
        return {
            "command": self.command,
            "workspace_id": self.workspace_id,
            "gpu": self.machine_type,
            "pip_packages": self.pip_packages if self.pip_packages is not None else [],
            "apt_packages": self.apt_packages if self.apt_packages is not None else [],
            "docker_image": self.docker_image,
            "framework": self.framework,
            "framework_version": self.framework_version,
            "python2": self.python2,
            "git_commit_hash": self.commit_hash,
            "description": self.description,
            "environment_vars": self.envvars,
            "attached_resources": self.attached_resources,
            "conda_file": self.conda_file,
            "run_type": self.run_type,
            "cwd": self.cwd,
            "root_directory": self.root_directory,
            "idempotent": self.idempotent,
            "provider": self.provider,
            "workflow_id": self.workflow_id,
            "commit_label": self.commit_label,
            "github_url": self.github_url,
            "github_ref": self.github_ref,
            "distributed": self.distributed,
        }


class RangeSpec:
    """A range parameter specification for hyperparameter search

    Attributes:
        min (:obj:`int` or :obj:`float`): the minimum value for the hyperparameter range
        max (:obj:`int` or :obj:`float`): the maximum value for the hyperparameter range
        scaling (:obj:`str`, optional): the scaling for the hyperparameter. Allowed values are
            :py:attr:`~HyperService.LINEAR`, :py:attr:`~HyperService.LOG`,
            :py:attr:`~HyperService.REVERSE_LOG`
        type (:obj:`str`, optional): the type for the hyperparameter. Allowed values are
            :py:attr:`~HyperService.INT`, :py:attr:`~HyperService.FLOAT`
    """

    def __init__(self, min, max, scaling=LINEAR, type=FLOAT):
        self.min = min
        self.max = max
        self.scaling = scaling
        self.type = type

    def to_payload(self):
        return {
            "min": self.min,
            "max": self.max,
            "scaling": self.scaling,
            "type": self.type,
        }


class ValueSpec:
    """A value parameter specification for hyperparameter search

    Attributes:
        values (:obj:`list` of :obj:`float`, :obj:`int`, or :obj:`str`): discrete values for
            this hyperparameter.
    """

    def __init__(self, values):
        self.values = values

    def to_payload(self):
        return {"values": self.values}

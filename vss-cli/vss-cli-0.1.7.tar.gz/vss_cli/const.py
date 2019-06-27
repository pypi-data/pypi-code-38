"""Constants used by VSS CLI (vss-cli)."""
import os

import pkg_resources

PACKAGE_NAME = "vss_cli"

__version__ = "0.1.7"

REQUIRED_PYTHON_VER = (3, 6, 4)

DEFAULT_TIMEOUT = 30
DEFAULT_ENDPOINT = "https://cloud-api.eis.utoronto.ca"
DEFAULT_ENDPOINT_NAME = "cloud-api"
DEFAULT_WEBDAV_SERVER = "https://vskey-stor.eis.utoronto.ca"
_LEGACY_CONFIG = ("~", ".vss-cli", "config.json")
_DEFAULT_CONFIG = ("~", ".vss-cli", "config.yaml")
_DEFAULT_HISTORY = ("~", ".vss-cli", "history")
LEGACY_CONFIG = os.path.expanduser(os.path.join(*_LEGACY_CONFIG))
DEFAULT_CONFIG = os.path.expanduser(os.path.join(*_DEFAULT_CONFIG))
DEFAULT_HISTORY = os.path.expanduser(os.path.join(*_DEFAULT_HISTORY))
DEFAULT_DATA_PATH = pkg_resources.resource_filename(PACKAGE_NAME, "data")
DEFAULT_CONFIG_TMPL = os.path.join(DEFAULT_DATA_PATH, "config.yaml")
DEFAULT_CHECK_UPDATES = True
DEFAULT_CHECK_MESSAGES = True

DEFAULT_TABLE_FORMAT = "simple"
DEFAULT_DATA_OUTPUT = "table"
DEFAULT_RAW_OUTPUT = "json"
DEFAULT_OUTPUT = "auto"
DEFAULT_VERBOSE = False
DEFAULT_DEBUG = False

DEFAULT_SETTINGS = {
    "endpoint": DEFAULT_ENDPOINT,
    "output": DEFAULT_OUTPUT,
    "table_format": DEFAULT_TABLE_FORMAT,
    "check_for_messages": DEFAULT_CHECK_MESSAGES,
    "check_for_updates": DEFAULT_CHECK_UPDATES,
    "timeout": DEFAULT_TIMEOUT,
    "verbose": DEFAULT_VERBOSE,
    "debug": DEFAULT_DEBUG,
}

DEFAULT_DATETIME_FMT = "%Y-%m-%d %H:%M"
SUPPORTED_DATETIME_FORMATS = ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M"]
GENERAL_SETTINGS = {
    "check_for_messages": bool,
    "check_for_updates": bool,
    "debug": bool,
    "verbose": bool,
    "default_endpoint_name": str,
    "output": str,
    "table_format": str,
    "timeout": int,
}

DEFAULT_HOST_REGEX = (
    "^[a-z][a-z0-9+\\-.]*://([a-z0-9\\"
    "-._~%!$&'()*+,;=]+@)?([a-z0-9\\-."
    "_~%]+|\\[[a-z0-9\\-._~%!$&'()*+,;"
    "=:]+\\])"
)

DEFAULT_NIC_DEL_MSG = (
    "Network adapter:\t{unit}\n"
    "Mac address:\t\t{macAddress}\n"
    "Network:\t\t{network[name]} ({network[moref]})\n"
    "Connected:\t\t{connected}\n"
)

DEFAULT_STATE_MSG = (
    "Host Name:\t{hostName} ({os[guestFullName]})\n"
    "IP Address:\t{ip_addresses}\n"
    "Are you sure you want to change the state from "
    '"{guestState} to {state}" '
    "of the above VM?"
)

DEFAULT_VM_DEL_MSG = (
    "Name:\t\t{name[name]}\n"
    "Folder:\t\t{folder_info[path]}\n"
    "Host Name:\t{hostName} "
    "({os[guestFullName]})\n"
    "IP Address:\t{ip_addresses}\n"
    "Are you sure you want to delete "
    "the above VM?"
)

COLUMNS_TWO_FMT = "{0:<20}: {1:<20}"

COLUMNS_DEFAULT = [("ALL", "*")]
COLUMNS_VM_MIN = [("UUID", "uuid"), ("NAME", "name")]
COLUMNS_VIM_REQUEST = [("UUID", "vm_uuid"), ("NAME", "vm_name")]
COLUMNS_MOID = [("MOREF", "moref"), ("NAME", "name")]
COLUMNS_FOLDER = [*COLUMNS_MOID, ("PARENT", "parent"), ("PATH", "path")]
COLUMNS_NET_MIN = [
    *COLUMNS_MOID,
    ("DESCRIPTION", "description"),
    ("SUBNET", "subnet"),
    ("PORTS", "ports"),
]
COLUMNS_NET = [
    *COLUMNS_NET_MIN,
    ("ACCESSIBLE", "accessible"),
    ("ADMIN", "admin"),
    ("ADMIN", "client"),
]
COLUMNS_PERMISSION = [
    ("PRINCIPAL", "principal"),
    ("GROUP", "group"),
    ("PROPAGATE", "propagate"),
]
COLUMNS_MIN = [
    ("ID", "id"),
    ("CREATED", "created_on"),
    ("UPDATED", "updated_on"),
]
COLUMNS_VSS_SERVICE = [
    ("ID", "id"),
    ("LABEL", "label"),
    ("NAME", "name"),
    ("GROUP", "group.name"),
]
COLUMNS_IMAGE = [("ID", "id"), ("PATH", "path"), ("NAME", "name")]
COLUMNS_OS = [("ID", "id"), ("GUESTID", "guestId"), ("NAME", "guestFullName")]
COLUMNS_REQUEST = [*COLUMNS_MIN, ("STATUS", "status")]
COLUMNS_REQUEST_MAX = [
    ("ERRORS", "message.errors[*]"),
    ("WARNINGS", "message.warnings[*]"),
    ("TASK", "task_id"),
    ("USER", "user.username"),
]
COLUMNS_REQUEST_IMAGE_SYNC_MIN = [*COLUMNS_REQUEST, ("TYPE", "type")]
COLUMNS_REQUEST_IMAGE_SYNC = [
    *COLUMNS_REQUEST,
    ("TYPE", "type"),
    ("DELETED", "deleted"),
    ("ADDED", "added"),
    *COLUMNS_REQUEST_MAX,
]
COLUMNS_REQUEST_SUBMITTED = [
    ("ID", "request.id"),
    ("STATUS", "request.status"),
    ("TASK ID", "request.task_id"),
    ("MESSAGE", "message"),
]
COLUMNS_REQUEST_SNAP = [
    ("DESCRIPTION", "snapshot.description"),
    ("ID", "snapshot.snap_id"),
    ("EXTENSIONS", "extensions"),
    ("ACTION", "action"),
    *COLUMNS_VIM_REQUEST,
    *COLUMNS_REQUEST_MAX,
]
COLUMNS_REQUEST_CHANGE_MIN = [
    *COLUMNS_REQUEST,
    *COLUMNS_VIM_REQUEST,
    ("APPROVED", "approval.approved"),
    ("ATTRIBUTE", "attribute"),
]
COLUMNS_REQUEST_CHANGE = [
    *COLUMNS_REQUEST_CHANGE_MIN,
    ("VALUE", "value[*]"),
    ("SCHEDULED", "scheduled_datetime"),
    *COLUMNS_REQUEST_MAX,
]
COLUMNS_REQUEST_EXPORT_MIN = [
    *COLUMNS_REQUEST,
    *COLUMNS_VIM_REQUEST,
    ("TRANSFERRED", "transferred"),
]
COLUMNS_REQUEST_EXPORT = [
    *COLUMNS_REQUEST_EXPORT_MIN,
    ("FILES", "files[*]"),
    *COLUMNS_REQUEST_MAX,
]
COLUMNS_REQUEST_FOLDER_MIN = [
    *COLUMNS_REQUEST,
    ("ACTION", "action"),
    ("MOREF", "moref"),
]
COLUMNS_REQUEST_FOLDER = [*COLUMNS_REQUEST_FOLDER_MIN, *COLUMNS_REQUEST_MAX]
COLUMNS_REQUEST_INVENTORY_MIN = [
    *COLUMNS_REQUEST,
    ("NAME", "name"),
    ("FORMAT", "format"),
]
COLUMNS_REQUEST_INVENTORY = [
    *COLUMNS_REQUEST_INVENTORY_MIN,
    ("PROPS", "properties.data[*]"),
    ("FILTERS", "filters"),
    ("HITS", "hits"),
    *COLUMNS_REQUEST_MAX,
]
COLUMNS_REQUEST_NEW_MIN = [
    *COLUMNS_REQUEST,
    *COLUMNS_VIM_REQUEST,
    ("APPROVED", "approval.approved"),
    ("BUILT", "built_from"),
]
COLUMNS_REQUEST_NEW = [
    *COLUMNS_REQUEST_NEW_MIN,
    ("DOMAIN", "domain"),
    ("SOURCE", "source_vm"),
    ("SOURCE", "source_template"),
    ("SOURCE", "source_image"),
    ("FOLDER", "folder"),
    ("CPU", "cpu"),
    ("MEMORY", "memory"),
    ("DISKS", "disks[*]"),
    ("NETWORKS", "networks[*]"),
    *COLUMNS_REQUEST_MAX,
]
COLUMNS_TK_MIN = [
    ("ID", "id"),
    ("CREATED", "created_on"),
    ("UPDATED", "updated_on"),
    ("LAST ACCESS", "last_access"),
    ("LAST IP", "ip_address"),
    ("VALID", "valid"),
]
COLUMNS_TK = [
    *COLUMNS_TK_MIN,
    ("TYPE", "type"),
    ("EXPIRATION", "expiration"),
    ("DURATION", "duration"),
]
COLUMNS_MESSAGE_MIN = [
    *COLUMNS_MIN,
    ("KIND", "kind"),
    ("SUBJECT", "subject"),
    ("STATUS", "status"),
]
COLUMNS_MESSAGE = [
    *COLUMNS_MIN,
    ("KIND", "kind"),
    ("STATUS", "status"),
    ("FROM", "user.username"),
    ("SUBJECT", "subject"),
    ("TEXT", "text"),
]
COLUMNS_VM = [
    *COLUMNS_VM_MIN,
    ("FOLDER", "folder"),
    ("CPU", "cpuCount"),
    ("MEMORY", "memoryGB"),
    ("POWER", "powerState"),
    ("GUEST", "guestFullName"),
    ("VERSION", "version"),
]
COLUMNS_VM_INFO = [
    ("UUID", "uuid"),
    ("NAME", "name.full_name"),
    ("FOLDER", "folder.path"),
    ("GUEST OS", "config.os.guestId"),
    ("VERSION", "hardware.version"),
    ("STATUS", "state.overallStatus"),
    ("STATE", "state.powerState"),
    ("ALARMS", "state.alarms"),
    ("CPU", "hardware.cpu.cpuCount"),
    ("MEMORY (GB)", "hardware.memory.memoryGB"),
    ("PROVISIONED (GB)", "storage.provisionedGB"),
    ("SNAPSHOT", "snapshot.exist"),
    ("DISKS", "hardware.devices.disks[*].unit"),
    ("NICS", "hardware.devices.nics[*].unit"),
    ("FLOPPY", "hardware.devices.floppies[*].unit"),
]
COLUMNS_VM_GUEST = [
    ("HOSTNAME", "hostName"),
    ("IP", "ipAddress[*]"),
    ("GUEST_NAME", "os.guestFullName"),
    ("GUEST_ID", "os.guestId"),
    ("TOOLS", "tools.runningStatus"),
]
COLUMNS_VM_GUEST_OS = [
    ("FAMILY", "guestFamily"),
    ("NAME", "guestFullName"),
    ("ID", "guestId"),
]
COLUMNS_VM_GUEST_IP = [
    ("IP", "ipAddress"),
    ("MAC", "macAddress"),
    ("ORIGIN", "origin"),
    ("STATE", "state"),
]
COLUMNS_VM_HAGROUP = [*COLUMNS_VM_MIN, ("VALID", "valid")]
COLUMNS_VM_MEMORY = [
    ("MEMORY_GB", "memoryGB"),
    ("HOTADD", "hotAdd.enabled"),
    ("HOTADD_LIMIT", "hotAdd.limitGB"),
    ("QUICKSTATS_BALLOONED", "quickStats.balloonedMemoryMB"),
    ("QUICKSTATS_USAGE", "quickStats.guestMemoryUsageMB"),
]
COLUMNS_VM_NIC_MIN = [
    ("LABEL", "label"),
    ("MAC", "macAddress"),
    ("TYPE", "type"),
    ("NETWORK", "network.name"),
    ("NETWORK_MOREF", "network.moref"),
    ("CONNECTED", "connected"),
]
COLUMNS_VM_NIC = [*COLUMNS_VM_NIC_MIN, ("START_CONNECTED", "startConnected")]
COLUMNS_OBJ_PERMISSION = [
    ("PRINCIPAL", "principal"),
    ("GROUP", "group"),
    ("PROPAGATE", "propagate"),
]
COLUMNS_VM_SNAP_MIN = [("ID", "id"), ("NAME", "name")]
COLUMNS_VM_SNAP = [
    *COLUMNS_VM_SNAP_MIN,
    ("SIZE_GB", "sizeGB"),
    ("DESCRIPTION", "description"),
    ("CREATED", "createTime"),
    ("AGE", "age"),
]
COLUMNS_VM_ADMIN = [("NAME", "name"), ("EMAIL", "email"), ("PHONE", "phone")]
COLUMNS_VM_ALARM_MIN = [
    *COLUMNS_MOID,
    ("STATUS", "overallStatus"),
    ("DATETIME", "dateTime"),
]
COLUMNS_VM_ALARM = [
    *COLUMNS_VM_ALARM_MIN,
    ("ACK", "acknowledged"),
    ("ACKBY", "acknowledgedByUser"),
    ("ACKDATE", "acknowledgedDateTime"),
]
COLUMNS_VM_BOOT = [
    ("ENTER_BIOS", "enterBIOSSetup"),
    ("BOOTRETRYDELAY", "bootRetryDelayMs"),
    ("BOOTDELAY", "bootDelayMs"),
]
COLUMNS_VM_CD_MIN = [
    ("LABEL", "label"),
    ("BACKING", "backing"),
    ("CONNECTED", "connected"),
]
COLUMNS_VM_CD = [
    *COLUMNS_VM_CD_MIN,
    ("CONTROLLER_TYPE", "controller.type"),
    ("CONTROLLER_NODE", "controller.virtualDeviceNode"),
]
COLUMNS_VM_CTRL_MIN = [
    ("LABEL", "label"),
    ("BUS_NUM", "busNumber"),
    ("TYPE", "type"),
]
COLUMNS_VM_CTRL = [
    *COLUMNS_VM_CTRL_MIN,
    ("CTRL KEY", "controllerKey"),
    ("SUMMARY", "summary"),
    ("SHARED_BUS", "sharedBus"),
    ("HOTADDREMOVE", "hotAddRemove"),
]
COLUMNS_VM_DISK_MIN = [
    ("LABEL", "label"),
    ("UNIT", "unit"),
    ("CONTROLLER", "controller.virtualDeviceNode"),
]
COLUMNS_VM_DISK = [
    *COLUMNS_VM_DISK_MIN,
    ("CAPACITY_GB", "capacityGB"),
    ("SHARES", "shares.level"),
]

COLUMNS_VM_DISK_BACKING = [
    *COLUMNS_VM_DISK,
    ("DESCRIPTOR", "descriptorFileName"),
    ("DEVICE_NAME", "deviceName"),
    ("DISK_MODE", "diskMode"),
    ("FILE", "fileName"),
    ("LUN", "lunUuid"),
    ("THIN", "thinProvisioned"),
]
COLUMNS_VM_CTRL_DISK = [
    ("CONTROLLER", "controller.virtualDeviceNode"),
    *COLUMNS_VM_DISK_MIN,
    ("CAPACITY_GB", "capacityGB"),
]
COLUMNS_VM_CPU = [
    ("CPU", "cpu"),
    ("CORES/SOCKET", "coresPerSocket"),
    ("HOTADD", "hotAdd.enabled"),
    ("HOTREMOVE", "hotRemove.enabled"),
    ("QUICKSTATS_DEMAND", "quickStats.overallCpuDemandMHz"),
    ("QUICKSTATS_USAGE", "quickStats.overallCpuUsageMHz"),
]
COLUMNS_VM_EVENT = [
    ("USERNAME", "userName"),
    ("CREATED", "createdTime"),
    ("MESSAGE", "message"),
]
COLUMNS_VM_STATE = [
    ("POWER", "powerState"),
    ("BOOT", "bootTime"),
    ("CONNECTION", "connectionState"),
    ("DOMAIN", "domain.name"),
]
COLUMNS_VM_TOOLS = [
    ("VERSION", "version"),
    ("STATUS", "versionStatus"),
    ("RUNNING", "runningStatus"),
]
COLUMNS_VM_HW = [
    ("VALUE", "value"),
    ("STATUS", "status"),
    ("UPGRADE_POLICY", "upgrade_policy.upgradePolicy"),
]
COLUMNS_EXTRA_CONFIG = [("KEY", "key"), ("VALUE", "value")]
COLUMNS_VSS_OPTIONS = [("OPTIONS", "[*]")]
COLUMNS_GROUP = [
    ("NAME", "cn"),
    ("DESCRIPTION", "description"),
    ("CREATED", "createTimestamp"),
    ("MODIFIED", "modifyTimestamp"),
    ("MEMBERS", "uniqueMemberCount"),
    ("MEMBER", "uniqueMember[*].uid"),
]
COLUMNS_GROUPS = [("GROUPS", "groups[*]")]
COLUMNS_ROLE = [
    ("NAME", "name"),
    ("DESCRIPTION", "description"),
    ("ENTITLEMENTS", "entitlements[*]"),
]
COLUMNS_USER_PERSONAL = [
    ("USERNAME", "username"),
    ("NAME", "full_name"),
    ("EMAIL", "email"),
    ("PHONE", "phone"),
    ("AUTH", "authTimestamp"),
    ("PWDCHANGE", "pwdChangeTime"),
    ("LOCKED", "pwdAccountLockedTime"),
]
COLUMNS_USER_STATUS = [
    ("CREATED", "created_on"),
    ("UPDATED", "updated_on"),
    ("LAST ACCESS", "last_access"),
    ("LAST IP", "ip_address"),
]
COLUMNS_MESSAGE_DIGEST = [("MESSAGE", "message")]
COLUMNS_NOT_REQUEST = [
    ("ALL", "all"),
    ("NONE", "none"),
    ("COMPLETION", "completion"),
    ("ERROR", "error"),
    ("SUBMISSION", "submission"),
]
COLUMNS_WEBDAV = [("FILES", "[*]")]
COLUMNS_WEBDAV_INFO = [
    ("CREATED", "created"),
    ("MODIFIED", "modified"),
    ("NAME", "name"),
    ("SIZE", "size"),
]
COLUMNS_SSH_KEY_MIN = [*COLUMNS_MIN, ("TYPE", "type"), ("COMMENT", "comment")]
COLUMNS_SSH_KEY = [
    *COLUMNS_SSH_KEY_MIN,
    ("FINGERPRINT", "fingerprint"),
    ("VALUE", "value"),
]

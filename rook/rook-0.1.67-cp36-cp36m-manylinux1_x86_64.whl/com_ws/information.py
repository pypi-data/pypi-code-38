import sys
import os
import platform
import socket

import six

from rook.config import VersionConfiguration, GitConfig
from rook import git
import rook.protobuf2.agent_info_pb2 as agent_info_pb

from rook.logger import logger


class Information(object):
    def collect(self):
        for name, collector in six.iteritems(self._collectors):
            try:
                if callable(collector):
                    value = collector()
                else:
                    value = collector
                setattr(self, name, value)
            except Exception as exc:
                logger.debug("Failed to collect %s information: %s", name, exc)

                setattr(self, name, "")
                pass

        return self


class SCMInformation(Information):
    def __init__(self):
        self._collectors = {
            'commit': self._get_commit,
            'origin': self._get_origin
        }

    def _get_commit(self):
        user_commit = GitConfig.GIT_COMMIT or os.environ.get('ROOKOUT_COMMIT', '')

        if user_commit:
            return user_commit
        else:
            git_root = self._get_git_root()

            if git_root:
                return git.get_revision(git_root)

        return ''

    def _get_origin(self):
        user_remote_origin = GitConfig.GIT_ORIGIN or os.environ.get('ROOKOUT_REMOTE_ORIGIN', '')

        if user_remote_origin:
            return user_remote_origin
        else:
            git_root = self._get_git_root()

            if git_root:
                return git.get_remote_origin(git_root)

        return ''

    def _get_git_root(self):
        return os.environ.get('ROOKOUT_GIT') or git.find_root(os.path.dirname(os.path.abspath(sys.argv[0])))


class NetworkInformation(Information):
    def __init__(self):
        self._collectors = {
            'ip_addr': self._get_ip_addr,
            'network': platform.node()
        }

    @staticmethod
    def _get_ip_addr():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))
        return s.getsockname()[0]


class SystemInformation(Information):
    def __init__(self):
        self._collectors = {
            'hostname': socket.gethostname,
            'os': platform.system,
            'os_version': self._get_os_version,
            # linux distro name on linux, blank otherwise
            'distro': lambda: platform.system() == 'Linux' and platform.linux_distribution()[0] or '',
            'arch': platform.machine()
        }

    def _get_os_version(self):
        system = platform.system()

        if system == 'Darwin':
            version = platform.mac_ver()[0]
        elif system == 'Linux':
            version = platform.linux_distribution()[1]
        elif system == 'Windows':
            version = platform.win32_ver()[0]
        else:
            version = ''

        return version


class VersionInformation(Information):
    def __init__(self):
        self._collectors = {
            'version': VersionConfiguration.VERSION,
            'commit': VersionConfiguration.COMMIT
        }


class PlatformInformation(Information):
    def __init__(self):
        self._collectors = {
            'platform': 'python',
            'version': sys.version,
            'variant': platform.python_implementation
        }


class AgentInformation(Information):
    def __init__(self):
        self._collectors = {
            'version': lambda: VersionInformation().collect(),
            'network': lambda: NetworkInformation().collect(),
            'system': lambda: SystemInformation().collect(),
            'platform': lambda: PlatformInformation().collect(),
            'scm': lambda: SCMInformation().collect(),
            'executable': lambda: sys.argv[0],
            'command_arguments': lambda: sys.argv[1:],
            'process_id': os.getpid
        }


def collect():
    return AgentInformation().collect()


def pack_agent_info(info):
    packed_info = agent_info_pb.AgentInformation()
    packed_info.agent_id = info.agent_id

    packed_info.version.CopyFrom(agent_info_pb.VersionInformation())
    packed_info.version.version = info.version.version
    packed_info.version.commit = info.version.commit

    packed_info.network.CopyFrom(agent_info_pb.NetworkInformation())
    packed_info.network.ip_addr = info.network.ip_addr
    packed_info.network.network = info.network.network

    packed_info.system.CopyFrom(agent_info_pb.SystemInformation())
    packed_info.system.hostname = info.system.hostname
    packed_info.system.os = info.system.os
    packed_info.system.os_version = info.system.os_version
    packed_info.system.distro = info.system.distro
    packed_info.system.arch = info.system.arch

    packed_info.platform.CopyFrom(agent_info_pb.PlatformInformation())
    packed_info.platform.platform = info.platform.platform
    packed_info.platform.version = info.platform.version
    packed_info.platform.variant = info.platform.variant

    packed_info.scm.CopyFrom(agent_info_pb.SCMInformation())
    packed_info.scm.commit = info.scm.commit
    packed_info.scm.origin = info.scm.origin

    packed_info.executable = info.executable
    packed_info.command_arguments.extend(info.command_arguments)

    packed_info.process_id = info.process_id

    for label_key, label_value in six.iteritems(info.labels):
        packed_info.labels[label_key] = label_value

    packed_info.tags.extend(info.tags)

    return packed_info

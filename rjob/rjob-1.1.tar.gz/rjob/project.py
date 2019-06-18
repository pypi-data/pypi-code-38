import asyncio
import json
import logging
import os
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import NamedTuple, Optional, Tuple

_unit_file = """[Unit]
Description=JOB one-shot service

[Service]
Type=exec
WorkingDirectory={wd}
StandardOutput=file:{logs}
StandardError=inherit
ExecStartPre=/bin/rm -rf {done}
ExecStartPre=/bin/mkdir -p {done}
ExecStart={exec}
{envs}
"""


def is_running(status):
    return status not in ('failed', 'not-found', 'dead')


def is_complete(status):
    return status in ('dead',)


def is_failed(status):
    return status in ('failed', 'not-found')


class Deployment(NamedTuple):
    name: str
    server: str
    server_user: str
    command: str  # {dir} - deployed directory
    install: str = ''
    local_directory: str = '.'
    remote_directory: Optional[str] = None
    result_directory: str = 'done'
    log_file: str = '.log'
    name_prefix: str = "job-"

    @property
    def deploy_dir(self):
        if self.remote_directory is not None:
            return self.remote_directory
        return '/tmp/jobs/' + self.name

    @property
    def complete_dir(self):
        return self.deploy_dir + "/" + self.result_directory

    @property
    def destination(self):
        return self.server_user + '@' + self.server

    @property
    def service_name(self):
        return self.name_prefix + self.name + ".service"

    async def deploy(self, deployment_index: int = 0, total_deployments: int = 1):
        log = logging.getLogger(self.name + "-" + self.server)
        # remove target dir
        log.info("removing outdated remote dir %s", self.deploy_dir)
        await self.exec_remote('rm', '-rf', self.deploy_dir)
        # create target dir
        log.info("create remote dir %s", self.deploy_dir)
        await self.exec_remote('mkdir', '-p', self.deploy_dir)
        await self.patch(deployment_index, total_deployments)

    async def patch(self, deployment_index: int = 0, total_deployments: int = 1):
        log = logging.getLogger(self.name + "-" + self.server)
        # check .jobignore file
        rsync = ['rsync', '-avz']
        if os.path.exists('.jobignore'):
            rsync += ['--exclude-from', '.jobignore']
        rsync += ['.', self.destination + ":" + self.deploy_dir]
        # call rsync
        log.info("synchronizing current dir to %s", self.deploy_dir)
        await self.exec_local(*rsync)
        # validate executable
        parts = list(self.command.split(' '))
        log.info("resolving binary %s", parts[0])
        binary = await self.call_remote('which', parts[0])
        log.info("binary %s resolved as %s", parts[0], binary)
        exec = " ".join([binary] + parts[1:])
        # install dependencies if required
        if self.install != '':
            await self.exec_remote('cd', self.deploy_dir, '&&', self.install)
        # create systemd unit file
        environ = [
            "Environment=RESULT=" + self.result_directory,
            "Environment=DEPLOYMENT_NUM=" + str(total_deployments),
            "Environment=DEPLOYMENT_INDEX=" + str(deployment_index)
        ]
        unit = _unit_file.format(
            wd=self.deploy_dir,
            exec=exec,
            done=self.result_directory,
            logs=self.remote_abs(self.log_file),
            envs="\n".join(environ),
        )
        # write to system files and disable (do not enable)
        log.info("creating %s", self.service_name)
        await self.push_file("/etc/systemd/system/" + self.service_name, unit)
        log.info("reloading daemons")
        await self.exec_remote('systemctl', 'daemon-reload')

    async def start(self):
        log = logging.getLogger(self.name + "-" + self.server)
        # stop
        await self.stop()
        # start service
        log.info("starting service %s", self.service_name)
        await self.exec_remote('systemctl', 'start', self.service_name)

    async def status(self):
        status = await self.call_remote('systemctl', 'show', '-p', 'SubState', '--value', self.service_name)
        return status

    async def stop(self):
        log = logging.getLogger(self.name + "-" + self.server)
        log.info("stopping service %s", self.service_name)
        await self.exec_remote('systemctl', 'stop', self.service_name)

    async def collect(self, to: str):
        log = logging.getLogger(self.name + "-" + self.server)
        to = to.format(deployment=self)
        log.info("making destination directory %s", to)
        os.makedirs(to, exist_ok=True)
        log.info("collecting results to %s", to)
        rsync = ['rsync', '-avz', self.destination + ":" + self.complete_dir + "/", to]
        await self.exec_local(*rsync)

    async def logs(self):
        with TemporaryDirectory() as cache_dir:
            rsync = ['rsync', '-avz', self.destination + ":" + self.remote_abs(self.log_file), cache_dir]
            await self.exec_local(*rsync)
            with open(cache_dir + "/" + self.log_file, 'rt') as f:
                for line in f:
                    yield line.strip()

    async def exec_remote(self, *args):
        ssh = [self.destination] + list(args)
        proc = await asyncio.create_subprocess_exec('ssh', *ssh)
        await proc.wait()
        assert proc.returncode == 0, " ".join(args)

    async def call_remote(self, *args):
        ssh = [self.destination] + list(args)
        proc = await asyncio.create_subprocess_exec('ssh', *ssh, stdout=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        assert proc.returncode == 0, " ".join(args)
        return stdout.decode().strip()

    async def push_file(self, destination, content):
        with NamedTemporaryFile() as file:
            file.write(content.encode())
            file.flush()
            rsync = ['rsync', '-avz', file.name, self.destination + ":" + destination]
            await self.exec_local(*rsync)

    async def exec_local(self, *args):
        proc = await asyncio.create_subprocess_exec(*args)
        await proc.wait()
        assert proc.returncode == 0, " ".join(args)

    def remote_abs(self, path):
        if path[0] == '/': return path
        return self.deploy_dir + "/" + path


class Project(NamedTuple):
    name: str
    servers: Tuple[str, ...]
    command: str
    install: str = ''

    def generate_deployments(self):
        ans = []
        for server in self.servers:
            user, server = server.split('@')
            ans.append(Deployment(
                name=self.name,
                server=server,
                server_user=user,
                command=self.command,
                install=self.install,
            ))
        return ans

    async def deploy(self):
        deployments = self.generate_deployments()
        tasks = []
        for idx, deployment in enumerate(deployments):
            task = deployment.deploy(idx, len(deployments))
            tasks.append(task)

        await asyncio.gather(*tasks)

    async def patch(self):
        deployments = self.generate_deployments()
        tasks = []
        for idx, deployment in enumerate(deployments):
            task = deployment.patch(idx, len(deployments))
            tasks.append(task)

        await asyncio.gather(*tasks)

    async def start(self):
        deployments = self.generate_deployments()
        tasks = []
        for deployment in deployments:
            task = deployment.start()
            tasks.append(task)
        await asyncio.gather(*tasks)

    async def stop(self):
        deployments = self.generate_deployments()
        tasks = []
        for deployment in deployments:
            task = deployment.stop()
            tasks.append(task)
        await asyncio.gather(*tasks)

    async def collect(self, to: str = 'complete/{deployment.server}'):
        deployments = self.generate_deployments()
        tasks = []
        for deployment in deployments:
            task = deployment.collect(to)
            tasks.append(task)
        await asyncio.gather(*tasks)

    async def statuses(self):
        deployments = self.generate_deployments()
        tasks = []
        for deployment in deployments:
            task = deployment.status()
            tasks.append(task)
        statuses = await asyncio.gather(*tasks)
        return tuple((deployments[i], status) for i, status in enumerate(statuses))

    async def wait(self, interval=2):
        log = logging.getLogger('main')
        deployments = self.generate_deployments()
        complete = []
        while True:
            tasks = []
            for deployment in deployments:
                task = deployment.status()
                tasks.append(task)
            statuses = await asyncio.gather(*tasks)
            deps = []
            for i, status in enumerate(statuses):
                if is_running(status):
                    deps.append(deployments[i])
                else:
                    complete.append((deployments[i], status))
            log.info("%s left deployments", len(deps))
            deployments = deps
            if len(deployments) == 0:
                break
            await asyncio.sleep(interval)
        return complete

    @staticmethod
    def load(file: str = 'deploy.json') -> 'Project':
        with open(file, 'rt') as f:
            return Project.from_dict(json.load(f))

    @staticmethod
    def from_dict(data: dict) -> 'Project':
        return Project(
            name=data['name'],
            command=data['command'],
            servers=data.get('servers', []),
            install=data.get('install', '')
        )

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'command': self.command,
            'servers': self.servers,
            'install': self.install,
        }

from typing import NamedTuple, Dict


class SupervisorScript:
    def start(self) -> str: raise NotImplementedError()

    def stop(self) -> str: raise NotImplementedError()

    def status(self) -> str: raise NotImplementedError()


class Basic(NamedTuple, SupervisorScript):
    name: str
    command: str
    workdir: str
    done: str
    logfile: str = '.log'
    environment: Dict[str, str] = {}

    @property
    def pidfile(self):
        return self.workdir + '/.pid'

    def start(self) -> str:
        script = ""
        for k, v in self.environment.items():
            script += "export " + k + "=" + repr(v) + "\n"
        script += 'cd {!r}\n'.format(self.workdir)
        script += 'rm -rf {done!r}\nmkdir -p {done!r}\n'.format(done=self.done)
        exec_cmd = 'sleep 3; {command}; rm -rf {pidfile}'.format(
            command=self.command,
            pidfile=self.pidfile,
        )
        script += 'nohup sh -c {exec!r} > {logfile!r} &\necho $! > {pidfile}\n'.format(
            exec=exec_cmd,
            logfile=self.logfile,
            pidfile=self.pidfile,
        )
        return script

    def stop(self) -> str:
        script = "if [ ! -f {pid} ]; then exit 0; fi; \nPID=$(cat {pid});\n".format(pid=self.pidfile)
        script += "if [ $? -eq 0 ]; then kill -9 -`cat /proc/$PID/stat | awk '{{print $5}}'`; rm {pid}; else echo already stopped; fi".format(
            pid=self.pidfile)

        return script

    def status(self) -> str:
        script = "if [ -f {pidfile} ]; then echo active; else echo dead; fi".format(
            pidfile=self.pidfile
        )
        return script


class Systemd(NamedTuple, SupervisorScript):
    name: str
    command: str
    workdir: str
    done: str
    logfile: str = '.log'
    environment: Dict[str, str] = {}
    name_prefix: str = 'job-'

    @property
    def service_name(self):
        return self.name_prefix + self.name + ".service"

    def start(self) -> str:
        envs = []
        for k, v in self.environment.items():
            envs.append('Environment=' + k + '=' + v)
        _unit_file = """[Unit]
        Description=JOB one-shot service

        [Service]
        Type=exec
        WorkingDirectory={workdir}
        StandardOutput=file:{logfile}
        StandardError=inherit
        ExecStartPre=/bin/rm -rf {done}
        ExecStartPre=/bin/mkdir -p {done}
        ExecStart={exec}
        {envs}
        """.format(
            exec=self.command,
            workdir=self.workdir,
            logfile=self.logfile,
            done=self.done,
            envs="\n".join(envs)
        )
        _unit_file = "\n".join(line.strip() for line in _unit_file.splitlines())
        script = "cat - > /etc/systemd/system/{unit} <<<EOF\n".format(unit=self.service_name)
        script += _unit_file + "\nEOF\n"
        script += "\nsystemctl daemon-reload"
        script += "\nsystemctl start {unit}".format(unit=self.service_name)
        return script

    def stop(self) -> str:
        return "systemctl stop {}".format(self.service_name)

    def status(self) -> str:
        return 'systemctl show -p SubState --value {!r}'.format(self.service_name)


def get_supervisor(name: str, deployment) -> SupervisorScript:
    name = str(name).strip().lower()
    if name == 'basic': return Basic(
        name=deployment.name,
        command=deployment.command,
        workdir=deployment.deploy_dir,
        environment=deployment.environment,
        done=deployment.complete_dir,
        logfile=deployment.log_path,
    )
    if name == 'systemd': return Systemd(
        name=deployment.name,
        command=deployment.command,
        workdir=deployment.deploy_dir,
        environment=deployment.environment,
        done=deployment.complete_dir,
        logfile=deployment.log_path,
    )
    raise RuntimeError("unknown supervisor " + name)

import copy
from distutils.version import LooseVersion  # pylint: disable=E0401,E0611
import logging
from pathlib import Path
import socket
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Type,
    Union,
)

from ssh2.session import Session  # type: ignore  # pylint: disable=E0611

from .util import dict_deep_update
from .whiteprint import (
    ExecOutput,
    Whiteprint,
    WhiteprintError,
)


logger = logging.getLogger('marchitect.site_plan')


class Step:
    def __init__(
            self, whiteprint_cls: Type[Whiteprint],
            cfg: Optional[Dict[str, Any]] = None,
            alias: Optional[str] =None):
        self.whiteprint_cls = whiteprint_cls
        self.cfg: Dict[str, Any] = cfg or {}
        self.alias = alias


class SitePlan:
    """
    A site is a target machine. The plan is the ordered set of whiteprints to
    apply to the machine.
    """

    plan: List[Step] = []

    default_cfg: Dict[str, Any] = {}

    def __init__(
            self, user: str, hostname: str,
            connect_func: Callable[[], Session],
            cfg: Dict[Union[str, Type[Whiteprint]], Dict[str, Any]],
            rsrc_paths: List[Path]):
        """
        Args:
            user: The login user to use.
            hostname: The target host machine.
            connect_func: A fn that when called connects to the target host.
            cfg: Configurations for whiteprints.
            rsrc_paths: Paths to whiteprint resource folders. The path should
                contain sub-folders with names matching whiteprints.
        """
        self.user = user
        self.hostname = hostname
        self.connect_func = connect_func
        self.cfg = cfg
        for rsrc_path in rsrc_paths:
            assert rsrc_path.exists()
        self.rsrc_paths = rsrc_paths
        # Config extracted from target host
        self.target_host_cfg: Optional[Dict[str, Any]] = None
        self.logger = logging.getLogger(
            '{parent}.{name}.{target}'.format(
                parent=logger.name,
                name=self.__class__.__name__,
                target=self.hostname.replace('.', '_')
        ))

    @classmethod
    def from_private_key(
            cls, hostname: str, port: int, user: str, private_key: str,
            private_key_password: Optional[str],
            cfg: Dict[Union[str, Type[Whiteprint]], Dict[str, Any]],
            rsrc_paths: List[Path]) -> 'SitePlan':
        """
        Creates a SitePlan that connects to the target host via a private key.

        Args:
            private_key: Path to private key on disk.

        See :meth:`__init__` for other args.
        """
        def connect() -> Session:
            session = SitePlan._create_session(hostname, port)
            session.userauth_publickey_fromfile(
                user, private_key, private_key_password)
            session.set_blocking(False)
            return session
        return cls(user, hostname, connect, cfg, rsrc_paths)

    @classmethod
    def from_password(
            cls, hostname: str, port: int, user: str, password: str,
            cfg: Dict[Union[str, Type[Whiteprint]], Dict[str, Any]],
            rsrc_paths: List[Path]) -> 'SitePlan':
        """
        Creates a SitePlan that connects to the target host via a user & pass.

        Args:
            password: Password for the user.

        See :meth:`__init__` for other args.
        """
        def connect() -> Session:
            session = SitePlan._create_session(hostname, port)
            session.userauth_password(user, password)
            session.set_blocking(False)
            return session
        return cls(user, hostname, connect, cfg, rsrc_paths)

    @staticmethod
    def _create_session(hostname: str, port: int) -> Session:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((hostname, port))
        session = Session()
        session.handshake(sock)
        return session

    def _resolve_whiteprint_rsrc_path(
            self, whiteprint_cls: Type[Whiteprint]) -> Optional[Path]:
        if whiteprint_cls.name is None:
            return None
        for rsrc_path in self.rsrc_paths:
            p = rsrc_path / whiteprint_cls.name
            if p.exists():
                return p
        return None

    def _get_target_host_cfg(self, session: Session) -> Dict[str, Any]:
        if self.target_host_cfg is not None:
            return self.target_host_cfg
        target_vars_wp = Whiteprint(session)
        r = target_vars_wp.exec(
            'uname -r && '
            'lsb_release -sir && '
            'hostname && '
            'hostname -f && '
            'cat /proc/cpuinfo | grep processor | wc -l')
        vals = r.stdout.decode('utf-8').splitlines()
        self.target_host_cfg = dict(
            user=self.user,
            host=self.hostname,
            kernel=vals[0],
            distro=vals[1].lower(),
            distro_version=LooseVersion(vals[2]),
            hostname=vals[3],
            fqdn=vals[4],
            cpu_count=int(vals[5]),
        )
        return self.target_host_cfg

    def one_off_exec(self, cmd: str, stdin: Optional[bytes] = None,
                     error_ok: bool = False) -> ExecOutput:
        session = self.connect_func()
        wp = Whiteprint(session, None, None)
        try:
            return wp.exec(cmd, stdin=stdin, error_ok=error_ok)
        finally:
            session.disconnect()

    def execute(self, mode: str) -> None:
        session = self.connect_func()
        target_host_cfg = self._get_target_host_cfg(session)
        for step in self.plan:
            rsrc_path = self._resolve_whiteprint_rsrc_path(step.whiteprint_cls)
            site_cfg = copy.deepcopy(self.default_cfg)
            site_cfg['_target'] = target_host_cfg
            dict_deep_update(site_cfg, step.cfg)
            dict_deep_update(site_cfg, self.cfg.get(step.whiteprint_cls, {}))
            if step.alias is not None:
                dict_deep_update(site_cfg, self.cfg.get(step.alias, {}))
            self.logger.info(
                'Executing %s (%s)', step.whiteprint_cls.__name__, mode)
            whiteprint = step.whiteprint_cls(session, site_cfg, rsrc_path)
            try:
                whiteprint.execute(mode)
            except WhiteprintError as e:
                log_msg = e.log_msg()
                if log_msg is not None:
                    self.logger.error(log_msg)
                raise
        session.disconnect()

    def install(self) -> None:
        self.execute('install')

    def update(self) -> None:
        self.execute('update')

    def clean(self) -> None:
        self.execute('clean')

    def start(self) -> None:
        self.execute('start')

    def stop(self) -> None:
        self.execute('stop')

    def validate(self, mode: str) -> Optional[str]:
        session = self.connect_func()
        target_host_cfg = self._get_target_host_cfg(session)
        for step in self.plan:
            rsrc_path = self._resolve_whiteprint_rsrc_path(step.whiteprint_cls)
            site_cfg = copy.deepcopy(self.default_cfg)
            site_cfg['_target'] = target_host_cfg
            dict_deep_update(site_cfg, step.cfg)
            dict_deep_update(site_cfg, self.cfg.get(step.whiteprint_cls, {}))
            if step.alias is not None:
                dict_deep_update(site_cfg, self.cfg.get(step.alias, {}))
            self.logger.info(
                'Validating %s (%s)', step.whiteprint_cls.__name__, mode)
            whiteprint = step.whiteprint_cls(session, site_cfg, rsrc_path)
            res = whiteprint.validate(mode)
            if res is not None:
                self.logger.error(
                    '%s failed validation (%s): %s', step.whiteprint_cls.__name__,
                    mode, res)
                break
        session.disconnect()
        return res

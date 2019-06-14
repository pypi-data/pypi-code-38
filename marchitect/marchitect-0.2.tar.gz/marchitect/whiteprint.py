import copy
from pathlib import Path
import select
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    TypeVar,
)

import jinja2
# Hacks for mypy (ssh2 has no types)
import ssh2.exceptions  # type: ignore  # pylint: disable=W0611
import ssh2.session  # type: ignore  # pylint: disable=W0611
from ssh2.channel import Channel  # type: ignore  # pylint: disable=E0611
from ssh2.fileinfo import FileInfo  # type: ignore  # pylint: disable=E0611
from ssh2.error_codes import LIBSSH2_ERROR_EAGAIN  # type: ignore  # pylint: disable=E0611
from ssh2.exceptions import (  # pylint: disable=E0611
    ChannelError,
    SCPProtocolError,
)
from ssh2.session import (  # pylint: disable=E0611
    LIBSSH2_SESSION_BLOCK_INBOUND,
    LIBSSH2_SESSION_BLOCK_OUTBOUND,
    Session,
)

from .prefab import Prefab
from .util import dict_deep_update


class ExecOutput:
    """The output of an executed program."""

    def __init__(self, exit_status: int, stdout: bytes, stderr: bytes):
        self.exit_status = exit_status
        self.stdout = stdout
        self.stderr = stderr

    def __repr__(self) -> str:
        return 'ExitStatus({!r}, {!r}, {!r})'.format(
            self.exit_status,
            self.stdout[-100:],
            self.stderr[-100:],
        )


def wait_session(session: Session, timeout: float=1) -> Tuple[bool, bool]:
    """
    Waits for at most timeout seconds for data to be available for reading, or
    for write pipe to available for writing.

    Returns:
        - Element 0: Whether there's data to read.
        - Element 1: Whether write to stdin could progress (I think....)
    """
    directions = session.block_directions()
    if directions == 0:
        return False, False
    read_fds = [session.sock] \
        if (directions & LIBSSH2_SESSION_BLOCK_INBOUND) else []
    write_fds = [session.sock] \
        if (directions & LIBSSH2_SESSION_BLOCK_OUTBOUND) else []
    res = select.select(read_fds, write_fds, (), timeout)
    assert len(res[2]) == 0, 'Unhandled exceptional fds'
    return len(res[0]) > 0, len(res[1]) > 0


T = TypeVar('T')


def retry_eagain(f: Callable[..., T], *args: Any) -> T:
    """
    Helper to retry libssh2 functions if they return an EAGAIN error.

    Args:
        f: Function that requires no arguments to call.
    """
    ret = f(*args)
    while ret == LIBSSH2_ERROR_EAGAIN:
        ret = f(*args)
    return ret


class WhiteprintError(Exception):
    def log_msg(self) -> str:
        raise NotImplementedError


class RemoteFileNotFoundError(WhiteprintError):
    """
    Raised when downloading a file via SCP fails because it does not exist.
    """
    def __init__(self, msg: str, inner: SCPProtocolError):
        super().__init__(msg, inner)
        self.msg = msg
        self.inner = inner

    def log_msg(self) -> str:
        return self.msg


class RemoteTargetDirError(WhiteprintError):
    """
    Raised when uploading a file via SCP fails because the target directory
    does not exist.
    """
    def __init__(self, msg: str, inner: SCPProtocolError):
        super().__init__(msg, inner)
        self.msg = msg
        self.inner = inner

    def log_msg(self) -> str:
        return self.msg


class RemoteExecError(WhiteprintError):
    """
    Raised when the remote exec returned a non-zero exit status.
    """
    def __init__(self, cmd: str, exec_output: ExecOutput):
        super().__init__(cmd, exec_output)
        self.cmd = cmd
        self.exec_output = exec_output

    def log_msg(self) -> str:
        stdout = self.exec_output.stdout.decode('utf-8', 'ignore')
        stderr = self.exec_output.stderr.decode('utf-8', 'ignore')
        return (
            'Remote Exec Failed: {}\n'
            'exit status: {}\n'
            'stdout: {}\n'
            'stderr: {}\n'
        ).format(
            self.cmd,
            self.exec_output.exit_status,
            stdout,
            stderr,
        )


class Whiteprint:
    """
    Subclass and implement the execute() method.

    The purpose of the whiteprint is to encapsulate the logic for various
    operation modes on a target host (install, update, clean, start, stop,
    ...). The logic will tend to be a mixture of shell commands run remotely,
    and file creation/modification with template variable substitution.

    Whiteprints do not manage the opening and closing of session objects.
    """

    # The name is used to look up the folder containing rsrcs for this
    # whiteprint by the siteplan.
    name: Optional[str] = None

    default_cfg: Dict[str, Any] = {}

    required_cfg: List[str] = []

    prefabs: List[Prefab] = []

    def __init__(
            self, session: Session, site_cfg: Optional[Dict[str, Any]] = None,
            rsrc_path: Optional[Path] = None) -> None:
        """
        Args:
             session: Must be set to non-blocking mode. This class will not
                close the session when finished, that's up to the caller.
             rsrc_path: Path to the location where relative-path specified
                resources can be found.
        """
        assert session.get_blocking() is False
        self.session = session
        self.cfg: Dict[str, Any] = copy.deepcopy(self.default_cfg)
        if site_cfg is not None:
            self.cfg.update(site_cfg)
        self.rsrc_path = rsrc_path
        assert self.rsrc_path is None or self.rsrc_path.exists()

        for required_key in self.required_cfg:
            if required_key not in self.cfg:
                raise KeyError('Cfg {!r} must be set'.format(required_key))

        computed_prefabs = self._compute_prefabs(self.cfg)
        if computed_prefabs:
            self.prefabs = self.prefabs[:] + computed_prefabs

    @classmethod
    def _compute_prefabs(cls, cfg: Dict[str, Any]) -> List[Prefab]:  # pylint: disable=W0613
        return []

    def exec(self, cmd: str, stdin: Optional[bytes] = None,
             error_ok: bool = False) -> ExecOutput:
        """
        Executes cmd in a session channel.

        This function collects std{out,err} in non-blocking mode to prevent
        the std{out,err} pipes from becoming full and blocking further
        execution of the cmd.

        stdin pipe is explicitly closed after being written to.

        Args:
            cmd: Executed in the context of a shell.
            stdin: Standard input to program.
            error_ok: If true, does not raise a RemoteExecError if exist status
                is non-zero.
        """
        chan = retry_eagain(self.session.open_session)
        try:
            retry_eagain(lambda: chan.execute(cmd))  # type: ignore
        except ChannelError:  # pylint: disable=W0706
            # TODO: Figure out what errors can arise.
            raise
        if stdin is not None:
            chan.write(stdin)
        chan.send_eof()

        stdout = b''
        stdout_done = False
        stderr = b''
        stderr_done = False
        while True:
            res = retry_eagain(
                lambda: wait_session(self.session, 0.1))
            if res[0]:
                if not stdout_done:
                    size, data = chan.read()
                    while size > 0:
                        stdout += data
                        size, data = chan.read()
                    if size == 0:
                        stdout_done = True
                    elif size != LIBSSH2_ERROR_EAGAIN:
                        assert False, 'Unexpected can read error: %d' % size
                else:
                    # Sanity check
                    assert chan.read()[0] == 0

                if not stderr_done:
                    size, data = chan.read_stderr()
                    while size > 0:
                        stderr += data
                        size, data = chan.read_stderr()
                    if size == 0:
                        stderr_done = True
                    elif size != LIBSSH2_ERROR_EAGAIN:
                        assert False, 'Unexpected can read error: %d' % size
                else:
                    # Sanity check
                    assert chan.read_stderr()[0] == 0

            res = chan.wait_eof()
            if res == LIBSSH2_ERROR_EAGAIN:
                # Process still running
                continue
            elif res == 0:
                if not stdout_done:
                    size, data = chan.read()
                    while size > 0:
                        stdout += data
                        size, data = chan.read()
                    if size == 0:
                        stdout_done = True
                    else:
                        assert False, 'Unexpected final read error: %d' % size
                if not stderr_done:
                    size, data = chan.read_stderr()
                    while size > 0:
                        stderr += data
                        size, data = chan.read_stderr()
                    if size == 0:
                        stderr_done = True
                    else:
                        assert False, 'Unexpected final read error: %d' % size
                assert stdout_done
                assert stderr_done
                # Need to wait for a successful close (0) to get the exit code.
                assert retry_eagain(chan.close) == 0
                exec_output = ExecOutput(chan.get_exit_status(), stdout, stderr)
                if exec_output.exit_status != 0 and not error_ok:
                    raise RemoteExecError(cmd, exec_output)
                else:
                    return exec_output
            else:
                assert False, 'Unexpected wait_eof value: {}'.format(res)

    def _resolve_rsrc(self, raw_path: str) -> Path:
        raw_path_obj = Path(raw_path)
        if raw_path_obj.is_absolute():
            return raw_path_obj
        else:
            assert self.rsrc_path is not None, \
                'Need rsrc_path for lookup of %r but none set.' % raw_path
            resolved_path = self.rsrc_path / raw_path_obj
            assert resolved_path.exists(), 'Could not find rsrc %r' % raw_path
            return resolved_path

    def _scp_send64_helper(
            self, dest_path: str, mode: int, size: int, mtime: int, atime: int
            ) -> Channel:
        try:
            return retry_eagain(self.session.scp_send64,
                dest_path, mode & 0o777, size, mtime, atime)
        except SCPProtocolError as e:
            # Unfortunately, very coarse error without any more info. It very
            # possibly occurs in other circumstances as well.
            assert e.args == ()
            raise RemoteTargetDirError('%r is a bad path.' % dest_path, e)

    def _scp_recv2_helper(self, src_path: str) -> Tuple[Channel, FileInfo]:
        try:
            # Hack for mypy
            scp_recv2: Callable[..., Tuple[Channel, FileInfo]] = \
                self.session.scp_recv2
            return retry_eagain(scp_recv2, src_path)
        except SCPProtocolError as e:
            # Unfortunately, very coarse error without any more info. It very
            # possibly occurs in other circumstances as well.
            assert e.args == ()
            raise RemoteFileNotFoundError('%r not found.' % src_path, e)

    def scp_up(self, src_path: str, dest_path: str,
               mode: Optional[int] = None) -> None:
        """
        Args:
            src_path: A path on the local filesystem.
            dest_path: A path on the remote filesystem.
            mode: The ACL for the new destination file. If omitted, uses the
                ACL on the source file.
        """
        src_path_obj = self._resolve_rsrc(src_path)
        fileinfo = src_path_obj.stat()
        if mode is None:
            mode = fileinfo.st_mode
        chan = self._scp_send64_helper(
            dest_path, mode, fileinfo.st_size, int(fileinfo.st_mtime),
            int(fileinfo.st_atime))
        with src_path_obj.open('rb') as f:
            for data in f:
                mv_data = memoryview(data)
                while True:
                    sent, expected = chan.write(bytes(mv_data))
                    if sent == LIBSSH2_ERROR_EAGAIN:
                        continue
                    if sent < expected:
                        mv_data = mv_data[sent:]
                    else:
                        assert sent == expected
                        break
        chan.close()

    def scp_down(self, src_path: str, dest_path: str) -> None:
        """
        Args:
            src_path: A path on the remote filesystem.
            dest_path: A path on the local filesystem.
        """
        chan, fileinfo = self._scp_recv2_helper(src_path)
        expected_size = fileinfo.st_size
        with open(dest_path, 'wb') as f:
            while True:
                size, data = chan.read()
                while size == LIBSSH2_ERROR_EAGAIN:
                    size, data = chan.read()
                if size == expected_size + 1:
                    f.write(data[:-1])
                    retry_eagain(chan.close)
                    return
                else:
                    f.write(data)
                    expected_size -= size

    def scp_up_from_bytes(
            self, data: bytes, dest_path: str, mode: int = 0o664) -> None:
        """
        Create a new file at the destination from bytes in memory.

        Args:
            data: The contents for the new destination file.
            dest_path: A path on the remote filesystem.
            mode: The ACL for the new destination file. If omitted, uses the
                ACL on the source file.
        """
        assert isinstance(data, bytes)

        def chunks(l: bytes, n: int) -> Iterable[bytes]:
            n = max(1, n)
            return (l[i:i + n] for i in range(0, len(l), n))
        # Goal: mtime/atime to be set to the current time on the target
        # machine. Solution: Setting mtime/atime to 0 seems to work.
        chan = self._scp_send64_helper(
            dest_path, mode, len(data), 0, 0)
        # TODO: Find optimal chunk size.
        for chunk in chunks(data, 32_000):
            mv_chunk = memoryview(chunk)
            while True:
                sent, expected = chan.write(bytes(mv_chunk))
                if sent == LIBSSH2_ERROR_EAGAIN:
                    continue
                if sent < expected:
                    mv_chunk = mv_chunk[sent:]
                else:
                    assert sent == expected
                    break
        chan.close()

    def scp_down_to_bytes(self, src_path: str) -> bytes:
        """
        Download a file from the destination to memory.

        Args:
            src_path: A path on the remote filesystem.

        Returns:
            Contents of the requested file.
        """
        chan, fileinfo = self._scp_recv2_helper(src_path)
        expected_size = fileinfo.st_size

        data = b''
        while True:
            size, chunk = chan.read()
            while size == LIBSSH2_ERROR_EAGAIN:
                size, chunk = chan.read()
            if size == expected_size + 1:
                data += chunk[:-1]
                retry_eagain(chan.close)
                return data
            else:
                data += chunk
                expected_size -= size

    def _resolve_cfg(
            self, cfg_override: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if cfg_override is not None:
            cfg = copy.deepcopy(self.cfg)
            dict_deep_update(cfg, cfg_override)
        else:
            cfg = self.cfg
        return cfg

    def scp_up_template(
            self, src_path: str, dest_path: str, mode: Optional[int] = None,
            cfg_override: Optional[Dict[str, Any]] = None) -> None:
        """
        Args:
            src_path: Path to a jinja template file. Variable substitution will
                be done before upload.
            cfg_override: Additional configuration variables with precedence
                over those of this whiteprint.
        See :meth:`src_up`.
        """
        cfg = self._resolve_cfg(cfg_override)
        src_path_obj = self._resolve_rsrc(src_path)
        if mode is None:
            fileinfo = src_path_obj.stat()
            mode = fileinfo.st_mode

        with src_path_obj.open() as f:
            template_contents = f.read()
        template = jinja2.Template(template_contents)
        rendered_template = template.render(cfg).encode('utf-8')
        self.scp_up_from_bytes(rendered_template, dest_path, mode)

    def scp_up_template_from_str(
            self, template_contents: str, dest_path: str, mode: int = 0o664,
            cfg_override: Optional[Dict[str, Any]] = None) -> None:
        cfg = self._resolve_cfg(cfg_override)
        template = jinja2.Template(template_contents)
        rendered_template = template.render(cfg).encode('utf-8')
        self.scp_up_from_bytes(rendered_template, dest_path, mode)

    def execute(self, mode: str) -> None:
        for prefab in self.prefabs:
            prefab.execute(self, mode)
        try:
            self._execute(mode)
        except NotImplementedError:
            pass

    def _execute(self, mode: str) -> None:
        """
        To be implemented by inheriting class.

        Execute receives a mode (install, update, clean ...) and is expected
        to run the appropriate deployment commands.
        """
        raise NotImplementedError

    def validate(self, mode: str) -> Optional[str]:
        for prefab in self.prefabs:
            res = prefab.validate(self, mode)
            if res is not None:
                return res
        try:
            return self._validate(mode)
        except NotImplementedError:
            return None

    def _validate(self, mode: str) -> Optional[str]:
        raise NotImplementedError


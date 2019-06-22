import typing as t
import sys
import logging
import asyncio
import signal
from functools import partial
from collections import defaultdict
from asyncio.subprocess import Process
from . import aioutils


logger = logging.getLogger(__name__)

# types :
uid = t.NewType("uid", str)
outtype = t.NewType("outtype", str)  # "stdout" | "stderr"

Row = t.Tuple[uid, Process, outtype, str]
FeedFunc = t.Callable[[uid, Process, outtype], t.AsyncIterator[Row]]
DisplayFunc = t.Callable[[t.AsyncIterator[Row]], t.Awaitable[None]]


class _Supervisor:
    def __init__(self, *, loop: asyncio.AbstractEventLoop) -> None:
        self.ps: t.List[Process] = []
        self.loop = loop
        self.on_init()  # xxx:

    def on_init(self) -> None:
        self.loop.add_signal_handler(
            signal.SIGINT, partial(self.send_signal, signal.SIGINT)
        )
        self.loop.add_signal_handler(
            signal.SIGTERM, partial(self.send_signal, signal.SIGTERM)
        )

    def watch(self, p: Process) -> None:
        self.ps.append(p)

    def send_signal(self, sig: int) -> None:
        logger.info("send signal (%s)", sig)
        for p in self.ps:
            try:
                p.send_signal(sig)
            except ProcessLookupError:
                logger.warning(
                    "send signal %s  -- ProcessLookupError -- pid=%s", sig, p.pid
                )

    def terminate(self) -> None:
        for p in self.ps:
            p.terminate()

    def kill(self) -> None:
        for p in self.ps:
            p.kill()


async def feed(
    _uid: t.Optional[uid], p: Process, attr: outtype, *, encoding: str = "utf-8"
) -> t.AsyncIterator[Row]:
    _uid = _uid or uid(str(p.pid))

    reader = getattr(p, attr)
    if reader is None:
        return

    async for line in reader:
        if not line:
            break
        yield (_uid, p, attr, line.decode(encoding).rstrip())


async def display_plain(aiter: t.AsyncIterator[Row]) -> None:
    async for (uid, p, typ, line) in aiter:
        if typ == "stderr":
            out = sys.stderr
        else:
            out = sys.stdout
        print(f"{uid[:12]:<12} {line}", file=out)
        out.flush()


async def display_colorful(aiter: t.AsyncIterator[Row]) -> None:
    colors = [
        36,  # CYAN
        35,  # MAGENTA
        32,  # GREEN
        34,  # BLUE
        33,  # YELLOW
        31,  # RED
    ] + [
        96,  # LIGHT CYAN_EX
        95,  # LIGHT MAGENTA_EX
        92,  # LIGHT GREEN_EX
        94,  # LIGHT BLUE_EX
        93,  # LIGHT YELLOW_EX
        91,  # LIGHT RED_EX
    ]
    cmap: t.DefaultDict[str, int] = defaultdict(lambda: colors[len(cmap) % len(colors)])
    async for (uid, p, typ, line) in aiter:
        if typ == "stderr":
            print(
                f"\x1b[{cmap[uid]}m{uid[:12]:<12} \x1b[90m{line}\x1b[0m",
                file=sys.stderr,
            )
            sys.stderr.flush()
        else:
            print(f"\x1b[{cmap[uid]}m{uid[:12]:<12} \x1b[0m{line}\x1b[0m")
            sys.stdout.flush()


# alias
display = display_colorful


def _iter_commands_with_normalized_style(
    xs: t.Union[
        t.List[t.Tuple[str, t.List[str]]], t.List[t.List[str]], t.Dict[str, t.List[str]]
    ]
) -> t.List[t.Tuple[uid, t.List[str]]]:
    """
    create format like below:
    [0] foo <cmd>
    [1] bar <cmd>
    """

    def _gen_uid(i, name, *, fmt="[{i:>%d}] {name}" % (len(str(len(xs))))):
        return uid(fmt.format(i=i, name=name))

    if not xs:
        return []
    elif isinstance(xs, dict) and hasattr(xs, "items"):
        return [(_gen_uid(i, name), cmd) for i, (name, cmd) in enumerate(xs.items())]
    elif isinstance(xs, list) and xs and isinstance(xs[0], (list, tuple)):
        if len(xs[0]) >= 2 and isinstance(xs[0][1], (list, tuple)):
            return [
                (_gen_uid(i, row[0]), row[1])  # type: ignore
                for i, row in enumerate(xs)
            ]
        else:
            return [
                (_gen_uid(i, cmd[0]), cmd)  # type: ignore
                for i, cmd in enumerate(xs)
            ]
    else:
        raise ValueError("unexpected input")


async def run(
    cmds: t.List[t.Tuple[uid, t.List[str]]],
    *,
    feed: FeedFunc = feed,
    display: DisplayFunc = display,
    loop: t.Optional[asyncio.AbstractEventLoop] = None,
    shell: bool = False,
) -> None:
    loop = loop or asyncio.get_event_loop()
    suprvisor = _Supervisor(loop=loop)
    q: asyncio.Queue[Row] = asyncio.Queue()

    async with aioutils.consuming(q, display) as asend:
        futs: t.List[t.Awaitable[t.Any]] = []

        for name, code in cmds:
            logger.debug("too: spawn name=%s, code=%r", name, code)
            if shell:
                p = await asyncio.create_subprocess_shell(
                    " ".join(code),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
            else:
                p = await asyncio.create_subprocess_exec(
                    *code,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

            suprvisor.watch(p)

            futs.append(asend(feed(name, p, outtype("stdout"))))  # type: ignore
            futs.append(asend(feed(name, p, outtype("stderr"))))  # type: ignore
            futs.append(p.wait())

        await asyncio.wait(futs)


def too(
    cmds: t.Union[
        t.List[t.Tuple[str, t.List[str]]], t.List[t.List[str]], t.Dict[str, t.List[str]]
    ],
    *,
    feed: FeedFunc = feed,
    display: DisplayFunc = display,
    debug: bool = True,
    shell: bool = False,
) -> None:
    coro = run(
        _iter_commands_with_normalized_style(cmds),
        display=display if sys.stdout.isatty() else display_plain,
        feed=feed,
        shell=shell,
    )
    aioutils.run(coro, debug=debug)

    if debug:

        async def _shutdown_check() -> None:
            current_task = asyncio.current_task()
            assert not [t for t in asyncio.all_tasks() if t != current_task]

        aioutils.run(_shutdown_check(), debug=debug)

VERSION = (0, 5, 8)

__title__ = 'serverchecks'
__version_info__ = VERSION
__version__ = '.'.join([str(a) for a in VERSION])
__author__ = 'Pawel Krawczyk'
__license__ = 'MIT'
__copyright__ = 'Copyright 2019 Pawel Krawczyk'

import asyncio
from timeit import default_timer as timer
from typing import List, Coroutine, Optional


class Outcome:
    """
    Class used to return results of both a single test (e.g. DNS) as well as series of tests.
    """

    def __init__(self, status: bool, info: str, summary: Optional[str] = None) -> None:
        self.status: bool = status
        self.info: str = info
        self.summary: Optional[str] = summary if summary is not None else ""

    def __str__(self) -> str:
        status = u"\u2713" if self.status else u"\u2717"
        return f'{status} {self.summary} {self.info}'


async def run_alerts(alerts: List[Coroutine]) -> None:
    await asyncio.gather(*alerts)


async def run_checks(checks: List[Coroutine]) -> Outcome:
    start = timer()
    results = await asyncio.gather(*checks)
    stop = timer()

    ok_tasks = [1 if a.status else 0 for a in results]

    summary = f'{len(checks)} tests completed in {stop - start:.2f} seconds'

    output = ''
    output += f'{sum(ok_tasks)} successful, {len(checks) - sum(ok_tasks)} failed\n'

    for res in results:
        output += str(res) + '\n'

    return Outcome(len(checks) == len(ok_tasks), output, summary)

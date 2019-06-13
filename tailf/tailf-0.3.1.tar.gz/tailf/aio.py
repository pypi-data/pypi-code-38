import asyncio

from .base import TailBase

__all__ = ["Tail"]


class Tail(TailBase):
    """Follows file appends and truncations. Asynchronous API.

    `Tail` objects mock read-only file objects mostly, except EOF is not
    considered a real thing.
    """

    async def _wait(self):
        await asyncio.sleep(0.01)  # TODO inotify

    async def readline(self):
        """Read until newline or truncation.

        Returns a string with newline character, when newline is encountered.

        If the file was truncated before newline, returns the rest of the file
        before truncation (if available). Keeps returning empty string until
        truncation flag is consumed with `get_truncated()`.
        """
        data = []
        while True:
            self._do_read1()
            if not self._buffer:
                if self._truncated:
                    assert self._truncation_handled is False, "invariant"
                    return self._decode(b"".join(data))
                await self._wait()
                continue

            newline = self._buffer.find(b"\n")
            if newline >= 0:
                newline += 1
                data.append(self._buffer.pop(newline))
                return self._decode(b"".join(data))
            else:
                data.append(self._buffer.pop())

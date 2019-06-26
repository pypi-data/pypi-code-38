from __future__ import annotations
from abc import ABCMeta, abstractmethod
from typing import AsyncIterator, Optional
import zlib
from .streaming import bytes_writer, bytes_reader


class Compressor(metaclass=ABCMeta):
    """A class to represent the methods available on a compressor"""

    @abstractmethod
    def compress(self, buf: bytes) -> bytes:
        ...

    def flush(self) -> bytes:
        ...


def make_gzip_compressobj() -> Compressor:
    """Make a compressor for 'gzip'

    :return: A gzip compressor.
    """
    return zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)


def make_deflate_compressobj() -> Compressor:
    """Make a compressor for 'deflate'

    :return: A deflate compressor.
    """
    return zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS)


def make_compress_compressobj() -> Compressor:
    """Make a compressor for 'compress'

    :return: A compress compressor.

    Note: This is not used by browsers anymore and should be avoided.
    """
    return zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS)


async def compression_writer_adapter(
        writer: AsyncIterator[bytes],
        compressobj: Compressor
) -> AsyncIterator[bytes]:
    """Adaptes a bytes generator to generated compressed output.

    :param writer: The writer to be adapted.
    :param compressobj: A compressor
    :return: A generator producing compressed output.
    """
    async for buf in writer:
        yield compressobj.compress(buf)
    yield compressobj.flush()


def compression_writer(
        buf: bytes,
        compressobj: Compressor,
        chunk_size: int = -1
) -> AsyncIterator[bytes]:
    """Create an async generator for compressed content.

    :param buf: The bytes to compress
    :param compressobj: The compressor.
    :param chunk_size: An optional chunk size where -1 indicates no chunking.
    :return: An sync generator of compressed bytes.
    """
    return compression_writer_adapter(bytes_writer(buf, chunk_size), compressobj)


class Decompressor(metaclass=ABCMeta):
    """A class to represent the methods available on a compressor"""

    @property
    @abstractmethod
    def unused_data(self) -> bytes:
        ...

    @property
    @abstractmethod
    def unconsumed_tail(self) -> bytes:
        ...

    @property
    @abstractmethod
    def eof(self) -> bool:
        ...

    @abstractmethod
    def decompress(self, buf: bytes, max_length: int = 0) -> bytes:
        ...

    @abstractmethod
    def flush(self, length: Optional[int] = None) -> bytes:
        ...

    @abstractmethod
    def copy(self) -> Decompressor:
        ...


def make_gzip_decompressobj() -> Decompressor:
    """Make a compressor for 'gzip'

    :return: A gzip compressor.
    """
    return zlib.decompressobj(zlib.MAX_WBITS | 16)


def make_deflate_decompressobj() -> Decompressor:
    """Make a compressor for 'deflate'

    :return: A deflate compressor.
    """
    return zlib.decompressobj(-zlib.MAX_WBITS)


def make_compress_decompressobj() -> Decompressor:
    """Make a compressor for 'compress'

    :return: A compress compressor.

    Note: This is not used by browsers anymore and should be avoided.
    """
    return zlib.decompressobj(9, zlib.DEFLATED, zlib.MAX_WBITS)


async def compression_reader_adapter(
        reader: AsyncIterator[bytes],
        decompressobj: Decompressor
) -> AsyncIterator[bytes]:
    async for item in reader:
        yield decompressobj.decompress(item)
    yield decompressobj.flush()


async def compression_reader(source: AsyncIterator[bytes], decompressobj: Decompressor) -> bytes:
    return await bytes_reader(compression_reader_adapter(source, decompressobj))

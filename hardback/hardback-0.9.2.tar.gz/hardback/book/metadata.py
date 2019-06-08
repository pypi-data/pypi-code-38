"""
Return a dictionary representing the header block - a block in JSON
representing metadata about the file.
"""

from ..util import chunk_sequence, hasher
import datetime
import os
import pathlib


def metadata(desc, source):
    stat = os.stat(source)
    block_count, rem = divmod(stat.st_size, desc.qr.block_size)
    block_count += bool(rem)

    c, r = desc.dimensions
    metadata_every = chunk_sequence.guess_metadata_every(c * r)
    chunk_count = 1 + block_count + (block_count // metadata_every)

    return {
        'block': {'count': block_count, 'size': desc.qr.block_size},
        'chunk': {'count': chunk_count, 'size': desc.qr.chunk_size},
        'dimensions': desc.dimensions,
        'file_bytes': stat.st_size,
        'file_name': pathlib.Path(source).name,
        'sha256': hasher.hash_file(source).hexdigest(),
        'timestamp': str(datetime.datetime.utcfromtimestamp(stat.st_mtime)),
    }


def format(sha256, **metadata):
    return FORMAT.format(s1=sha256[:32], s2=sha256[32:], **metadata)


FORMAT = """\
<pre>


file_name: {file_name}
file_bytes: {file_bytes}
timestamp: '{timestamp}'
sha256: "\\
  {s1}\\
  {s2}\\
"
block: {{count: {block[count]},  size: {block[size]}}}
chunk: {{count: {chunk[count]},  size: {chunk[size]}}}
dimensions: {dimensions}
</pre>
"""

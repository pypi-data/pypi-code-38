from ..qr.write import write
from ..util import files
import itertools
import math
import os
import yaml


def write_chunks(hc):
    desc = hc.hardback.desc
    digits = math.ceil(math.log(hc.metadata['block']['count'], 16))
    os.makedirs(desc.qr_image_dir, exist_ok=True)
    suffix = desc.qr.SUFFIX
    file_format = os.path.join(
        desc.qr_image_dir, f'{hc.index}-%0{digits}x{suffix}'
    )

    document = bytes.fromhex(hc.metadata['sha256'])
    metadata_block = yaml.dump(hc.metadata).encode()
    file_blocks = files.file_blocks(hc.source, desc.qr.block_size)
    blocks = itertools.chain((metadata_block,), file_blocks)

    for index, block in enumerate(blocks):
        yield write(desc.qr, file_format % index, index, document, block)

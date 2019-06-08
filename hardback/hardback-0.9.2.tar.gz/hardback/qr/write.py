import segno
import struct


def write(qr, out, index, document, block):
    document = document[: qr.document_bytes]
    index = struct.pack(f'>q', index)[: qr.index_bytes]
    data = index + document + block

    def write(fp):
        q = segno.make_qr(data, version=qr.version, error=qr.error)
        q.save(fp)
        return fp.name

    if len(data) > qr.chunk_size:
        raise ValueError(f'{len(data)} > chunk_size {qr.chunk_size}')
    if not isinstance(out, str):
        return write(out)

    if not out.endswith(qr.SUFFIX):
        out += qr.SUFFIX

    with open(out, 'wb') as fp:
        return write(fp)

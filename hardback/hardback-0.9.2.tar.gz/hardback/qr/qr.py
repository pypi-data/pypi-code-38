import attr
from . import codes, constants


@attr.s(slots=True)
class QR:
    version = attr.ib(default=0)
    error = attr.ib(default='')
    block_size = attr.ib(default=0)
    document_bytes = attr.ib(default=8)
    index_bytes = attr.ib(default=8)

    SUFFIX = '.png'

    @property
    def max_chunk_size(self):
        return getattr(codes.CODES[self.version - 1].binary, self.error)

    @property
    def chunk_size(self):
        return self.block_size + self.document_bytes + self.index_bytes

    def check_chunk_size(self):
        if self.chunk_size > self.max_chunk_size:
            raise ValueError(
                'Not enough space for chunk: %d > %d'
                % (self.chunk_size, self.max_chunk_size)
            )

    @error.validator
    def check_error(self, _, error):
        if error and error not in constants.ERRORS:
            raise ValueError

    @version.validator
    def check_version(self, _, version):
        if version and not (1 <= version <= constants.MAX_VERSION):
            raise ValueError

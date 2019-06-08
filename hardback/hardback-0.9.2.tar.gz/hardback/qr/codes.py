from attr import dataclass, Factory
from .raw_codes import RAW_CODES


@dataclass(slots=True)
class ECC:
    L: int = 0
    M: int = 0
    Q: int = 0
    H: int = 0


@dataclass(slots=True)
class Code:
    index: int = 0
    pixels: int = 0
    data: ECC = Factory(ECC)
    numeric: ECC = Factory(ECC)
    alphanumeric: ECC = Factory(ECC)
    binary: ECC = Factory(ECC)
    kanji: ECC = Factory(ECC)

    @staticmethod
    def make(index, pixels, *eccs):
        return Code(index, pixels, *(ECC(*i) for i in eccs))


CODES = tuple(Code.make(*i) for i in RAW_CODES)

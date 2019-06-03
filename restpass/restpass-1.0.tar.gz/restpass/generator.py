from seedrandom import Seed


class Generator:
    def __init__(self, source: str):
        self._source = source
        self._salt = []

        self._alphabet = None
        self.set_rules(digits=True, lowercase=True, uppercase=True)

    def set_rules(self, digits: bool = True, lowercase: bool = True, uppercase: bool = True, symbols: bool = False):
        self._alphabet = ""

        if digits:
            self._alphabet += "0123456789"
        if lowercase:
            self._alphabet += "abcdefghijklmnopqrstuvwxyz"
        if uppercase:
            self._alphabet += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if symbols:
            self._alphabet += "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"

    def set_custom_alphabet(self, alphabet: str):
        self._alphabet = alphabet

    def set_salt(self, *args):
        for arg in args:
            if not isinstance(arg, bytes):
                raise TypeError(f"{arg} is not instance of bytes")

        self._salt = args

    def generate(self, length: int):
        if length <= 0:
            raise ValueError("Length must be > 0")

        string = ""
        for letter_index in range(length):
            # Generate random index for each position and fetch char from alphabet
            seed = Seed(self._source.encode("utf-8"),
                        self._alphabet.encode("utf-8"),  # "".join(sorted(self._alphabet)).encode("utf-8") TODO for v1.1
                        str(length).encode("utf-8"),
                        str(letter_index).encode("utf-8"),
                        *self._salt)  # hashlib.sha256 by default

            random_index = seed.randint(_min=0, _max=len(self._alphabet) - 1)
            string += self._alphabet[random_index]

        return string

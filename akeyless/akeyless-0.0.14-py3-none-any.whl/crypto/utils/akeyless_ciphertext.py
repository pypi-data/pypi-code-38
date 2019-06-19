import base64
import struct

from akeyless.crypto.utils.algorithms import CryptoAlgorithm


class AkeylessCiphertext(object):
    AKEYLESS_VERSION = 1
    AKEYLESS_VERSION_BYTES_LEN = 1
    KEY_VERSION_BYTES_LEN = 4
    HEADER_DD_LEN = 2

    @staticmethod
    def serialize(alg, key_version, derivations_data, encrypted_data):
        # type: (CryptoAlgorithm, int, list, bytes) -> AkeylessCiphertext
        obj = AkeylessCiphertext()
        obj._serialize(alg, key_version, derivations_data, encrypted_data)
        return obj

    @staticmethod
    def deserialize(alg, cipher_bytes):
        # type: (CryptoAlgorithm, bytes) -> AkeylessCiphertext
        obj = AkeylessCiphertext()
        obj._deserialize(alg, cipher_bytes)
        return obj

    @property
    def encrypted_data(self):
        return self._encrypted_data

    def get_derivations_data(self, num_of_fragments):
        if not self._alg.is_deterministic() and len(self._derivations_data) is 1:
            dd_list = []
            for i in range(0, num_of_fragments):
                dd_list.append(self._derivations_data[0])
            return dd_list

        if len(self._derivations_data) is not num_of_fragments:
            raise ValueError("The number of derivations data does not match the number of the key fragments")

        return self._derivations_data

    def to_base64(self):
        # type: () -> str
        return base64.b64encode(self._cipher_bytes)

    def to_str(self):
        # type: () -> str
        return self.to_base64()

    def to_bytes(self):
        # type: () -> bytes
        return self._cipher_bytes

    @staticmethod
    def extract_key_version_from_cipher(cipher_bytes):
        # type: (bytes) -> int
        akeyless_version_len = AkeylessCiphertext.AKEYLESS_VERSION_BYTES_LEN
        key_version_len = AkeylessCiphertext.KEY_VERSION_BYTES_LEN
        key_version = struct.unpack_from(">i", cipher_bytes[akeyless_version_len:
                                                            akeyless_version_len+key_version_len])[0]
        if key_version < 1:
            raise ValueError("Invalid key version")
        return key_version

    def _serialize(self, alg, key_version, derivations_data, encrypted_data):
        # type: (CryptoAlgorithm, int, list, bytes) -> None
        self._alg = alg
        self._akeyless_version = self.AKEYLESS_VERSION
        self._key_version = key_version
        self._set_dd_by_alg(alg, derivations_data)
        self._encrypted_data = encrypted_data
        self._cipher_bytes = self._serialize_cipher_bytes()

    def _set_dd_by_alg(self, alg, derivations_data):
        # type: (CryptoAlgorithm, list) -> None
        if not derivations_data:
            raise ValueError("No derivation data was provided")

        if alg.is_deterministic():
            self._derivations_data = derivations_data
            return
        self._derivations_data = [derivations_data[0]]

    def _serialize_cipher_bytes(self):
        # type: () -> bytes
        combined_dd = self._serialize_derivations_data()
        return bytes(struct.pack(">b", self.AKEYLESS_VERSION_BYTES_LEN) +
                     struct.pack(">i", self._key_version)) + combined_dd + self._encrypted_data

    def _serialize_derivations_data(self):
        # type: () -> bytes
        if self._alg.is_deterministic():
            raise Exception("Unsupported")  # TODO
        return self._serialize_dd_for_nondeterministic_alg()

    def _serialize_dd_for_nondeterministic_alg(self):
        # type: () -> bytes
        if not self._derivations_data:
            raise ValueError("No derivation data was provided")
        dd = self._derivations_data[0]
        num_of_dd = 1
        return bytes(struct.pack(">b", len(dd)) + struct.pack(">b", num_of_dd)) + dd

    def _deserialize(self, alg, cipher_bytes):
        # type: (CryptoAlgorithm, bytes) -> None
        self._alg = alg
        self._cipher_bytes = cipher_bytes
        if cipher_bytes is None or len(cipher_bytes) is 0:
            raise ValueError("Empty ciphertext")

        parsed_bytes = 0
        parsed_bytes += self._parse_akeyless_version(cipher_bytes, parsed_bytes)
        parsed_bytes += self._parse_key_version(cipher_bytes, parsed_bytes)
        parsed_bytes += self._parse_derivations_data(cipher_bytes, parsed_bytes)
        parsed_bytes += self._parse_encrypted_data(cipher_bytes, parsed_bytes)

    def _parse_akeyless_version(self, cipher_bytes, offset):
        # type: (bytes, int) -> int
        self._akeyless_version = struct.unpack_from("<b", cipher_bytes[offset:self.AKEYLESS_VERSION_BYTES_LEN])[0]
        if self._akeyless_version < 1:
            raise ValueError("Invalid cipher version")

        return self.AKEYLESS_VERSION_BYTES_LEN

    def _parse_key_version(self, cipher_bytes, offset):
        # type: (bytes, int) -> int
        self._key_version = struct.unpack_from(">i", cipher_bytes[offset:offset+self.KEY_VERSION_BYTES_LEN])[0]
        if self._key_version < 1:
            raise ValueError("Invalid key version")

        return self.KEY_VERSION_BYTES_LEN

    def _parse_derivations_data(self, cipher_bytes, offset):
        # type: (bytes, int) -> int
        if self._alg.is_deterministic():
            raise Exception("Unsupported")  # TODO
        return self._parse_dd_for_nondeterministic_alg(cipher_bytes, offset)

    def _parse_dd_for_nondeterministic_alg(self, cipher_bytes, offset):
        # type: (bytes, int) -> int

        if cipher_bytes is None or len(cipher_bytes) - offset < self.HEADER_DD_LEN:
            raise ValueError("No derivation data was provided")

        dd_len = struct.unpack_from("<b", cipher_bytes[offset:offset+1])[0]
        num_of_dd = struct.unpack_from("<b", cipher_bytes[offset+1:offset+2])[0]
        if num_of_dd is not 1:
            raise ValueError("Invalid number of derivations data for non-deterministic algorithm")

        if len(cipher_bytes) - offset < dd_len * num_of_dd + self.HEADER_DD_LEN:
            raise ValueError("Invalid serialized derivations data length")

        dd_st_indx = offset + self.HEADER_DD_LEN
        dd = cipher_bytes[dd_st_indx:dd_st_indx + dd_len]
        self._derivations_data = [dd]
        return self.HEADER_DD_LEN + dd_len

    def _parse_encrypted_data(self, cipher_bytes, offset):
        # type: (bytes, int) -> int
        self._encrypted_data = cipher_bytes[offset:]
        return len(cipher_bytes) - offset

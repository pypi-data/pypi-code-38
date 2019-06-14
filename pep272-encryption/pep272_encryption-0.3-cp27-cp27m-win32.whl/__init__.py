#!python3
"""\
This module creates PEP-272 cipher object classes for building block ciphers
in python.

To use, inherit the PEP272Cipher and overwrite
``encrypt_block`` or ``decrypt_block(self, key, string, **kwargs)`` methods
and set the block_size attribute.


Example:

::

 class YourCipher(PEP272Cipher):
     block_size=8

     def encrypt_block(self, key, string, **kwargs):
         ...

     def decrypt_block(self, key_string, **kwargs):
         ...


"""

from .util import xor_strings, b_chr, b_ord
from .version import *


MODE_ECB = 1  #:
MODE_CBC = 2  #:
MODE_CFB = 3  #:
MODE_PGP = 4  #:
MODE_OFB = 5  #:
MODE_CTR = 6  #:


class PEP272Cipher(object):
    """
    A cipher class as defined in PEP-272_.

    Following parameters must be passed in every case:

    :param bytes key: The symmetric key to use for encryption.
    :param int mode: The mode of operation to use.\
        For valid values see Reference/:ref:`api-modes`.
    :param \\**kwargs: See below.
    
    Depending on the blockcipher mode of operation one or multiple of the
    following arguments must be passed depending on the mode of operation.

    :Keyword arguments:

        - **IV** or **iv** (`bytes`) -- \
            A unique bytestring with once the block size in \
            length. For security reasons it should be unpredictable and must \
            never be used twice for the same key. \
            \
            **Required for**: *CBC*, *CFB* and *OFB* modes. 

        * **segment_size** (`int`) -- \
            The segment size for one encryption "segment" of \
            CFB mode in bits. It must be multiple of 8 (only byte-sized \
            operations are allowed) and the maximum size is the block size. \
            \
            **Required for**: *CFB* mode.

        * **counter** (`callable`) -- \
            A callable object returning bytes with the \
            length of one block. For security reasons the output of the counter \
            must never be the same twice. \
            \
            **Required for**: *CTR* mode.


    Additional keyword arguments are passed to the underlying block cipher.

    .. _PEP-272: https://www.python.org/dev/peps/pep-0272/

    """
    block_size = NotImplemented
    IV = None

    def __init__(self, key, mode, **kwargs):
        "A cipher class as defined in PEP-272"
        if not key:
            raise ValueError("'key' cannot have a length of 0")
        self.key = key
        self.mode = mode
        self.IV = kwargs.pop('IV', None) or kwargs.pop('iv', None)
        self._status = self.IV

        self.segment_size = kwargs.pop('segment_size', 8)
        self._counter = kwargs.pop('counter', None)

        self.kwargs = kwargs

        self._check_arguments()
        self._keystream = self._create_keystream()


    def _check_arguments(self):
        """
        Checks if all required keyword arguments have been set.

        Tests for:
            - IV when using MODE_CBC, MODE_CFB, MODE_OFB
            - callable counter with MODE_CTR

        """
        if self.mode in (MODE_CBC, MODE_CFB, MODE_OFB, MODE_PGP):
            if self._status is None:
                raise TypeError("For CBC, CFB, PGP and OFB mode an IV is "
                                "required.")
            if len(self._status) != self.block_size and self.mode != MODE_PGP:
                raise ValueError("'IV' length must be block_size ({})".format(
                    self.block_size))
            elif self.mode == MODE_PGP:
                if not len(self._status) in (self.block_size, self.block_size+2):
                    raise ValueError(
                        ("'IV' length must be block_size ({})"
                         "or blocksize + 2".format(self.block_size)))

        if self.mode == MODE_CFB:
            if not self.segment_size:
                raise TypeError("missing required positional argument for CFB:"
                                " 'segment_size'")
            if not (8 <= self.segment_size <= self.block_size*8) or (
                    self.segment_size % 8):
                raise TypeError("segment_size must be between 8 and "
                                "block_size*8 and a multiple of 8")

        if self.mode == MODE_CTR:
            if self._counter is None:
                raise TypeError("missing required positional argument for CTR:"
                                " 'counter'")
            if not callable(self._counter):
                raise TypeError("counter must be a callable, it is not")


    def encrypt(self, string):
        """Encrypt data with the key and the parameters set at initialization.
    
        The cipher object is stateful; encryption of a long block
        of data can be broken up in two or more calls to `encrypt()`.
        That is, the statement:
            
            >>> c.encrypt(a) + c.encrypt(b)
        
        is always equivalent to:
        
             >>> c.encrypt(a+b)
        
        That also means that you cannot reuse an object for encrypting
        or decrypting other data with the same key.
        
        This function does not perform any padding.
        
         - For `MODE_ECB`, `MODE_CBC` *string* length
           (in bytes) must be a multiple of *block_size*.
        
         - For `MODE_CFB`, *string* length (in bytes) must be a multiple
           of *segment_size*/8.
        
         - For `MODE_CTR` and `MODE_OFB`, *string* can be of any length.
        
        :param bytes string: The piece of data to encrypt.
        :raises ValueError:
            When a mode of operation has be requested this code cannot handle.
        :raises ValueError:
            When len(string) has a wrong length, as described above.
        :raises TypeError:
            When the counter callable in CTR returns data with the wrong length.
            
        :return:
            The encrypted data, as a byte string. It is as long as
            *string*.
        :rtype: bytes
        """
        if self.mode in (MODE_OFB, MODE_CTR):
            return self._encrypt_with_keystream(string)

        out = []

        if self.mode == MODE_CFB:
            for block in _block(string, self.segment_size // 8):
                encrypted_iv = self.encrypt_block(self.key, self._status)
                ecd = xor_strings(encrypted_iv, block)

                iv_p1 = self._status[self.segment_size//8:]
                iv_p2 = ecd

                self._status = iv_p1 + iv_p2

                out.append(ecd)

        elif self.mode in (MODE_ECB, MODE_CBC):
            for block in _block(string, self.block_size):
                if self.mode == MODE_ECB:
                    ecd = self.encrypt_block(self.key, block, **self.kwargs)
                elif self.mode == MODE_CBC:
                    xored = xor_strings(self._status, block)
                    ecd = self._status = self.encrypt_block(self.key, xored,
                                                       **self.kwargs)

                out.append(ecd)

        else:
            raise ValueError("Unknown mode of operation")

        return b"".join(out)


    def decrypt(self, string):
        """Decrypt data with the key and the parameters set at initialization.
    
        The cipher object is stateful; decryption of a long block
        of data can be broken up in two or more calls to `decrypt()`.
        That is, the statement:
            
            >>> c.decrypt(a) + c.decrypt(b)
        
        is always equivalent to:
        
             >>> c.decrypt(a+b)
        
        That also means that you cannot reuse an object for encrypting
        or decrypting other data with the same key.
        
        This function does not perform any padding.
        
         - For `MODE_ECB`, `MODE_CBC` *string* length
           (in bytes) must be a multiple of *block_size*.
        
         - For `MODE_CFB`, *string* length (in bytes) must be a multiple
           of *segment_size*/8.
        
         - For `MODE_CTR` and `MODE_OFB`, *string* can be of any length.
        
        :param bytes string: The piece of data to decrypt.
        :raises ValueError:
            When a mode of operation has be requested this code cannot handle.
        :raises ValueError:
            When len(string) has a wrong length, as described above.
        :raises TypeError:
            When the counter callable in CTR returns data with the wrong length.
            
        :return:
            The decrypted data, as a byte string. It is as long as
            *string*.
        :rtype: bytes
        """
        if self.mode in (MODE_OFB, MODE_CTR):
            return self.encrypt(string)

        out = []

        if self.mode == MODE_CFB:
            for block in _block(string, self.segment_size // 8):
                encrypted_iv = self.encrypt_block(self.key, self._status)
                dec = xor_strings(encrypted_iv, block)

                iv_p1 = self._status[self.segment_size//8:]
                iv_p2 = block

                self._status = iv_p1 + iv_p2

                out.append(dec)

        elif self.mode in (MODE_ECB, MODE_CBC):
            for block in _block(string, self.block_size):
                if self.mode == MODE_ECB:
                    dec = self.decrypt_block(self.key, block, **self.kwargs)
                elif self.mode == MODE_CBC:
                    decrypted_but_not_xored = self.decrypt_block(self.key, block,
                                                                 **self.kwargs)
                    dec = xor_strings(self._status, decrypted_but_not_xored)
                    self._status = block

                out.append(dec)

        else:
            raise ValueError("Unknown mode of operation")

        return b"".join(out)

    def encrypt_block(self, key, block, **kwargs):
        """Dummy function for the encryption of a single block.
        Overwrite with 'real' encryption function.

        :param bytes key: The symmetric encryption key.
        :param bytes block: A single plaintext block to encrypt.
        :param \\**kwargs: Additional parameters passed to `__init__`.

        :raises NotImplementedError: This method is to be overridden.

        :returns: ciphertext block
        :rtype: bytes"""
        raise NotImplementedError

    def decrypt_block(self, key, block, **kwargs):
        """Dummy function for the decryption of a single block.
        Overwrite with 'real' deryption function.

        :param bytes key: The symmetric encryption key.
        :param bytes block: A single ciphertext block to encrypt.
        :param \\**kwargs: Additional parameters passed to `__init__`.

        :raises NotImplementedError: This method is to be overridden.

        :returns: plaintext block
        :rtype: bytes"""
        raise NotImplementedError

    def _encrypt_with_keystream(self, data):
        "Encrypts data with the set keystream."
        xor = [x ^ y for (x, y) in zip(map(b_ord, data),
                                              self._keystream)]
        return bytes(bytearray(xor))  # Faster


    def _create_keystream(self):
        "Creates a keystream (generator object) for OFB or CTR mode."
        if self.mode not in (MODE_OFB, MODE_CTR):
            # Coverage somehow does not work here
            return  # pragma: no cover

        while True:
            if self.mode == MODE_OFB:
                _next = self._status
            elif self.mode == MODE_CTR:
                _next = self._counter()
                if len(_next) != self.block_size:
                    raise TypeError("Counter length must be block_size")

            self._status = self.encrypt_block(self.key, _next, **self.kwargs)

            for k in self._status:
                yield b_ord(k)


def _block(bytestring, block_size):
    """Splits bytestring in block_size-sized blocks.

Raises an error if len(string) % blocksize != 0.
"""
    if block_size == 1:
        return map(b_chr, bytearray(bytestring))

    rest_size = len(bytestring) % block_size

    if rest_size:
        raise ValueError("Input 'bytestring' must be a multiple of block_size / "
                         "segment_size (CFB mode) in length")

    block_count = len(bytestring) // block_size

    return (
        bytestring[i * block_size:((i + 1) * block_size)]
        for i in range(block_count))

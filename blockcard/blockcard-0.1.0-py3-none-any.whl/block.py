import os
import traceback
import time
import sys
from hashlib import sha256
from datetime import datetime

use_colors = False
try:
    import colorama
    from colorama import Fore, Style
    colorama.init(autoreset=True)
    use_colors = True
except ImportError:
    traceback.print_exc()
    print(
        "Problem while importing terminal color library. "
        "You can install it using the appropriate version "
        "of pip with `pip install colorama`"
    )
except:
    traceback.print_exc()
    print(
        "Problem while initializing colorama. Continuing "
        "without colored output."
    )

class Block:
    headers = [
        ('parent_hash', 32),
        ('metadata_hash', 32),
        ('nonce', 32),
        ('timestamp', 8),
        ('difficulty', 1)
    ]

    def __init__(self, block_path=None, parent_path=None):
        self.total_header_size = sum(h[1] for h in Block.headers)
        for header, _ in self.headers:
            setattr(self, header, None)
        if parent_path or not block_path:
            if not parent_path:
                print("No parent path specified. Generating initial block")
                self.parent_hash = b'\x00' * 32
                self.nonce = b'\x00' * 32
            else:
                parent = Block(parent_path)
                self.parent_hash = parent.current_hash
                self.nonce = parent.nonce
            target_date = input('Timestamp? (YYYY-mm-dd): ')
            dt = datetime.strptime(target_date, '%Y-%m-%d')
            self.timestamp = int(dt.timestamp()).to_bytes(8, 'big')
            d = int(input("Difficulty (recipient age): "))
            self.set_bounds(d)
            self.difficulty = d.to_bytes(1, 'big')
            metadata_path = input("Path to metadata: ")
            print(("\n== Confirm input ==\n"
                   "Generating card for {} ({:.2f} days from now)\n"
                   "Recipient age at time of receipt: {} years\n"
                   "With message from file `{}`\n").format(
                        dt, (dt.timestamp() - time.time()) / (24 * 3600),
                        d,
                        metadata_path
            ))
            input("Press ENTER to confirm.")
            if not os.path.exists(metadata_path):
                raise FileNotFoundError("Invalid path: `{}`".format(metadata_path))
            with open(metadata_path, 'rb') as f:
                self.metadata = f.read()
            self.metadata_hash = hash(self.metadata)
            print("Finding nonce...")
            self.find_nonce()
            self.current_hash = hash(self.all_headers)

        elif block_path:
            if not os.path.exists(block_path):
                raise FileNotFoundError("The path `{}` does not exist".format(parent_path))
            if fsize(block_path) < self.total_header_size:
                raise ValueError(
                    "Size of file {} is too small "
                    "({}B is less than minimum 105B required)".format(
                        block_path, fsize(block_path)
                ))
            with open(block_path, 'rb') as f:
                bs = f.read()
                start = 0
                for h, l in self.headers:
                    setattr(self, h, bs[start:start + l])
                    start += l
                self.set_bounds(self.difficulty)
                self.metadata = bs[start:]
                self.current_hash = hash(bs[:self.total_header_size])
        self.check()

    def set_bounds(self, d):
        if isinstance(d, bytes):
            d = int.from_bytes(d, 'big')
        self.hash_lb = (2 ** (255 - d))        .to_bytes(32, 'big')
        self.hash_ub = (2 ** (255 - d + 1) - 1).to_bytes(32, 'big')

    @property
    def all_headers(self):
        return b''.join(getattr(self, h) for h, _ in self.headers)

    def find_nonce(self):
        d = int.from_bytes(self.difficulty, 'big')
        inonce = int.from_bytes(self.nonce, 'big')
        while True:
            inonce += 1
            self.nonce = inonce.to_bytes(32, 'big')
            if inonce % 2 ** 8 == 0:
                sys.stdout.write('\rNonce: {}'.format(self.nonce.hex()))
            h = hash(self.all_headers)
            if self.hash_lb <= h <= self.hash_ub:
                print()
                return

    def check(self, verbose=False):
        assert hash(self.metadata) == self.metadata_hash
        verbose and print("Metadata hash correct.")
        assert self.hash_lb <= hash(self.all_headers) <= self.hash_ub
        verbose and print("Current header hash correct.")

    def deep_check(self, verbose=False):
        if verbose:
            print("Checking `{}`".format(self.current_hash.hex()))
            print("\n{}\n".format(to_bitstring(self.current_hash)))
        self.check(verbose)
        if self.parent_hash == b'\x00' * 32:
            verbose and print("\nAll blocks in chain are valid!")
        else:
            try:
                b = Block(block_path='{}.bkc'.format(self.parent_hash.hex()))
                b.deep_check(verbose)
            except:
                traceback.print_exc()
                print("Failed to perform deep check while looking for block `{}.bkc`. Are you missing a .bkc file?".format(self.parent_hash.hex()))

    def __str__(self):
        return "\n".join([
            to_titlestring('Headers'),
            'Parent block: {}'.format(to_hexstring(self.parent_hash)),
            'Nonce:        {}'.format(to_hexstring(self.nonce)),
            'Metadata hash {}'.format(to_hexstring(self.metadata_hash)),
            'Timestamp:    {}'.format(to_timestring(self.timestamp)),
            'Difficulty:   {} ({:.2e} expected hashes)'.format(
                int.from_bytes(self.difficulty, 'big'),
                2 ** (int.from_bytes(self.difficulty, 'big') + 1)
            ),
            "",
            to_titlestring("Hash of this block\'s headers"),
            to_bitstring(self.current_hash),
            "",
            to_titlestring('Metadata'),
            self.metadata.decode('utf-8')
        ])

    def print(self):
        print(str(self))

    def save(self, dir_path=''):
        fname = "{}.bkc".format(self.current_hash.hex())
        with open(os.path.join(dir_path, fname), 'wb') as f:
            f.write(self.all_headers)
            f.write(self.metadata)
        return fname

def to_titlestring(s, use_colors=use_colors):
    if not use_colors:
        return '==' + s + '==\n'
    return '{}== {} =={}\n'.format(
        Style.BRIGHT,
        s,
        Style.RESET_ALL
    )

def to_hexstring(bs, use_colors=use_colors):
    if not use_colors:
        return bs.hex()
    result = ''
    for b in bs:
        if b % 2 == 0:
            result += Fore.CYAN
        else:
            result += Fore.MAGENTA
        b = bytes([b])
        result += b.hex()
        result += Fore.RESET
    return result

def to_bitstring(bs, use_colors=use_colors, indent=2):
    rows = []
    row = []
    for i, b in enumerate(bs, 1):
        row.append(format(b, "08b"))
        if i % 4 == 0:
            rows.append(' ' * indent + ' '.join(row))
            row = []
    no_color = '\n'.join(rows)
    if not use_colors:
        return no_color
    leading = True
    result = Style.BRIGHT
    for c in no_color:
        if leading:
            if c != '1':
                result += c
            else:
                leading = False
                result += Style.RESET_ALL
        if not leading:
            color = Fore.MAGENTA
            if c == '0':
                color = Fore.CYAN
            result += color
            result += c
            result += Fore.RESET
    return result


def fsize(block_path):
    return os.stat(block_path).st_size

def hash(bs):
    return sha256(sha256(bs).digest()).digest()

def to_timestring(bs):
    i = int.from_bytes(bs, byteorder='big')
    i = min(i, 2 ** 31)
    d = datetime.fromtimestamp(i)
    return str(d)


from string import ascii_uppercase
from itertools import product
from re import findall

class pythonCipher:


    def doCypher(self, orig):
        (encode, decode) = self.playfair("Playfair example")
        print("So, Original (updated) looks like this: " + orig)
        enc = encode(orig)
        print("Now, Encoded (updated):" + enc)
        print("And, Decoded (updated):" + decode(enc))

    def partition(self, seq, n):
        seqx = [seq[i : i + n] for i in range(0, len(seq), n)]
        return seqx

    def uniq(self, seq):
        seen = {}
        seenx = [seen.setdefault(x, x) for x in seq if x not in seen]
        return seenx

    """Instantiate a specific encoder/decoder."""

    def playfair(self, key, from_='J', to=None):
        if to is None:
            to = 'I' if from_ == 'J' else ''

        def canonicalize(s):
            return filter(str.isupper, s.upper()).replace(from_, to)

        # Building 5x5 matrix.
        m = self.partition(self.uniq(canonicalize(key + ascii_uppercase)), 5)

        # Generate all forward translations.
        enc = {}

        # Map pairs in same row.
        for row in m:
            for i, j in product(range(5), repeat=2):
                if i != j:
                    enc[row[i] + row[j]] = row[(i + 1) % 5] + row[(j + 1) % 5]

        # Map pairs in same column.
        for c in zip(*m):
            for i, j in product(range(5), repeat=2):
                if i != j:
                    enc[c[i] + c[j]] = c[(i + 1) % 5] + c[(j + 1) % 5]

        # Map pairs with cross-connections.
        for i1, j1, i2, j2 in product(range(5), repeat=4):
            if i1 != i2 and j1 != j2:
                enc[m[i1][j1] + m[i2][j2]] = m[i1][j2] + m[i2][j1]

        # Generate reverse translations.
        dec = dict((v, k) for k, v in enc.iteritems())

        def sub_enc(txt):
            lst = findall(r"(.)(?:(?!\1)(.))?", canonicalize(txt))
            return " ".join(enc[a + (b if b else 'X')] for a, b in lst)

        def sub_dec(encoded):
            return " ".join(dec[p] for p in self.partition(canonicalize(encoded), 2))

        return sub_enc, sub_dec

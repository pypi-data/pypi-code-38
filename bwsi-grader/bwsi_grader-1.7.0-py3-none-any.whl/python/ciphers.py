r"""
# Ciphers
Having fun with cryptographic functions for encrypting messages.

## Required Concepts
Control Flow
- basic usage of for-loops
- if/else statements

Basic Objects
- Built-in functions for strings
- Joining strings
- The modulo function

Sequence Types
- The built-in `index` function
- Indexing sequences
- Checking for membership in a sequence

## Caesar Cipher
A Caesar cipher is a cryptographic function that takes as input a plaintext string and outputs a ciphertext string that is the encoding of the input. Specifically, the Caesar cipher shifts each letter of the alphabet by some fixed amount, wrapping at the end of the alphabet and ignoring whitespace. For example, the string

```
CogWorks is fun
```

encoded using a Caesar cipher with shift 3 becomes

```
FrjZrunv lv ixq
```

Let's break down how this works. We'll order the alphabet so that lowercase letters come before capital letters. This gives us:

```
abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
```

The Caesar cipher will shift each letter by some amount. In our case, we chose to shift by 3 characters. This means we'll map `a` to `d`, `b` to `e`, ..., `w` to `z`, `x` to `A`, ... `W` to `Z`, `X` to `a`, `Y` to `b`, and `Z` to `c`. We can create a mapping just like this:

```
abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
defghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZabc
```

This is essentially what the Caesar cipher is doing. Now if we want to encode our string, we see that `C` maps to `F`, `o` maps to `r`, and so on.

Reversing the process to decode a string is quite straightforward. If we receive the encrypted string

```
Wlys yvjrz
```

and we know that it was encoded using a Caesar cipher with shift 7, we can easily create our reverse substitution alphabet:

```
hijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZabcdefg
abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
```

and decode the message:

```
Perl rocks
```

Fun fact: The ROT13 algorithm is a famous special case of the Caesar cipher. It assumes all letters are the same case. What's special about ROT13 is that it is its own inverse: you apply the exact same function to both encode and decode your string.

#### Breaking the Caesar Cipher
While not very secure, the Caesar cipher can be effective as a very weak form of encryption. Note that to break the encryption, we can simply try shift amounts from 1 through 25 and see which one comes out as correct English. This is a *brute-force* solution.

## Keyword Cipher
A keyword cipher (or substitution cipher) is another cryptographic function. Rather than shift the alphabet by some fixed amount like the Caesar cipher, the Keyword cipher shifts the alphabet based on a keyword or phrase. Let's illustrate with an example.

Suppose our keyphrase is

```
beaverworks is fun
```

and we want to encode the string

```
python rules
```

Like the Caesar cipher, we'll build a substitution alphabet. We'll go through our keyphrase and record the **unique** letters, in order, then append all the rest of the alphabet that wasn't in the keyphrase. For simplicity, we'll only use lowercase letters for this cipher.

Going through the keyphrase we pull out

```
beavrwrksicl
```

Note that each letter is unique, and is in the order we saw it in the keyphrase. The second 'e' we see in 'beaverworks' is simply ignored. Now all we have to do is go through the alphabet and append all the letters that we don't already have. This gives us the following mapping:

```
abcdefghijklmnopqrstuvwxyz
beavrwoksicldfghjmnpqtuxyz
```

Now we can make a straightforward substitution for each letter in our string, `'python rules'`, and get the encoded string

```
hypkgf mqlrn
```

Taking another example, if we receive the encoded string

```
kqbhj khsjhp kpjige
```

and we know that the keyword used to create the cipher was

```
massachusetts institute of technology
```

then we can easily assemble the substitution alphabet

```
abcdefghijklmnopqrstuvwxyz
maschuetinoflgybdjkpqrvwxz
```

and decode the string

```
super secret string
```

#### Breaking the Keyword Cipher
You might be thinking that this is more difficult to decrypt than our Caesar cipher if we don't know the keyword, and you'd be right. With the Caesar cipher, all we had to do to break it was try 25 different shifts and see which one came out in sensible English.

With the keyword cipher, there are `403,291,461,126,605,635,584,000,000` permutations of the alphabet. And this is with only lowercase letters! Even if we could check 2 billion permutations each second, it would take more than 6 billion years to try all the possible permutations here.

Practically, this is where things like frequency analysis come into play, where if we have enough encoded text we can look at the frequency of each letter and try to match these to known frequencies of English. For example, the letter 'e' is very common and if the frequency of 'q' in the encoded text is close to that known frequency, then 'q' probably maps to 'e'. Of course, there are many sophisticated techniques in cryptanalysis worth exploring.
"""

from typing import *


__seed__ = ["cesarcipher", "keywordcipher"]


def grade_cesar_cipher(student_func: Callable[[str, int], str]):
    """ Tests the student's solution to "Cesar Cipher"

    Parameters
    ----------
    student_func:Callable[[str, int], str]
       The student's solution function.
    """
    from bwsi_grader import compare_functions
    from bwsi_grader.print import print_passed
    from random import randint, choices
    import string
    from hashlib import sha224

    def encode_caesar_soln(string: str, shift_amt: int) -> str:
        ''' Encodes the specified `string` using a Caesar cipher with shift `shift_amt`

            Parameters
            ----------
            string : str
                The string to encode.

            shift_amt : int
                How much to shift the alphabet by.

            Returns
            -------
            str
                The encoded string.
           '''
        alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        return ''.join(alphabet[(alphabet.index(i)+shift_amt) % 52]
                       if i in alphabet else i for i in string)
    # pad
    # pad
    # pad
    # pad
    # pad
    # check for some standard cases
    for input_ in (('test', 4), ('CogWorks 2018', 5), ('Perl rocks', 7)):
        compare_functions(student_func, encode_caesar_soln, fn_args=input_)

    for i in range(100):
        test_str = ''.join(choices(string.ascii_letters + string.digits + ' ', k=randint(5, 50)))
        test_shft = randint(0, 52)
        compare_functions(student_func, encode_caesar_soln, fn_args=(test_str, test_shft))

    print_passed(sha224(str.encode(__seed__[0])).hexdigest())


def grade_keyword_cipher(student_func: Callable[[str, str], str]):
    """ Tests the student's solution to "Cesar Cipher"

    Parameters
    ----------
    student_func:Callable[[str, str], str]
       The student's solution function.
    """
    from bwsi_grader import compare_functions
    from bwsi_grader.print import print_passed
    from random import randint, choices
    import string
    from hashlib import sha224

    def encode_keyword_soln(string, keyword):
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        string = string.lower()
        keyword = ''.join(keyword.lower().split())
        from collections import OrderedDict
        sub_alphabet = ''.join(k for k in OrderedDict.fromkeys(keyword + alphabet))
        return ''.join(sub_alphabet[alphabet.index(c)] if c in alphabet else c for c in string)

    # pad
    # pad
    # pad
    # pad
    # pad
    # check for some standard cases
    for input_ in (('test', 'test'), ('cogworks 2018', 'python'), ('perl rocks', 'my key')):
        compare_functions(student=student_func, soln=encode_keyword_soln, fn_args=input_)

    for i in range(100):
        test_str = ''.join(choices(string.ascii_lowercase + string.digits + ' ', k=randint(5, 50)))
        kword = ''.join(choices(string.ascii_lowercase + ' ', k=randint(5, 50)))
        compare_functions(student=student_func, soln=encode_keyword_soln, fn_args=(test_str, kword))

    print_passed(sha224(str.encode(__seed__[1])).hexdigest())

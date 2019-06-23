import os

# dictonary mapping digits to their corresponding letters on a phone pad
digit_to_letters = {
    '0': '',
    '1': '',
    '2': 'ABC',
    '3': 'DEF',
    '4': 'GHI',
    '5': 'JKL',
    '6': 'MNO',
    '7': 'PQRS',
    '8': 'TUV',
    '9': 'WXYZ'}

digit_to_digit = {x: x for x in digit_to_letters}

# dictonary mapping letters + digits to their correspondings digits
letter_to_digit = {x: y for y in digit_to_letters for x in digit_to_letters[y]}
letter_to_digit.update(digit_to_digit)


def number_to_words(number, word_dict):
    '''takes a string representing a US phone number and returns a
    string with the numbers following the area code transformed into
    numbers and words. Phone numbers must be 10 digits or 11 digits,
    including a one as the first digit (eg. 1-123-456-7890).

    The function attempts to first find the transformation with longest words
    and then the ones with a lower number of words'''

    return next(wordifications(number, word_dict))


def all_wordifications(number, word_dict):
    '''takes a string representing a US phone number and dictionary
    mapping numbers to words. returns all combinations of words that
    can encode the phone number as a list of strings, preserving the
    area code as numbers. Will not include the original number.
    Phone numbers must be 10 characters with dashes (eg. 123-456-7890)
    or 11 characters with dashes, including a one (eg. 1-123-456-7890).

    By default a list of english words is used but an optional argument
    permits the use of other word lists.'''

    return [x for x in wordifications(number, word_dict)]


def wordifications(number, word_dict):
    '''wordification generator that takes a US phone number string with dashes'''
    pre_codes, remainder = split_number(number)
    for words in wordifications_search(''.join(remainder), word_dict):
        yield '-'.join(pre_codes + words)


def wordifications_search(dashless_number, word_dict):
    '''wordification generator that takes a number string, as well as a
    dictionary mapping strings of digits to words and yields a list of words
    that the original string can map to. Resulting strings with longer words
    being mapped are returned first. Words only containing digits will be
    merged concatenated into one string. This function will not yield the
    original input number'''

    n = len(dashless_number)
    queue = [(0, n, [])]

    # BFS to search for wordifications
    while queue:
        (i, j, words) = queue.pop(0)

        # find words fitting sub string digits
        for word in word_dict.get(dashless_number[i:j], []):

            # compress digits into last word if possible
            if i > 0 and words[-1].isdigit() and word.isdigit():
                new_words = words[:-1] + [words[-1] + word]
            else:
                new_words = words + [word]

            if j == n and not ''.join(new_words).isdigit():
                # yield resulting words list for  number if complete
                yield new_words
            else:
                # search for words to fill subsequent sub string digits
                queue.append((j, n, new_words))

        # after looking for longer words, look for shorter words
        if i < j - 1:
            queue.append((i, j - 1, words))


def words_to_number(number_words, dash=True):
    '''takes a wordified phone number string with dashes and returns a string with
    all the letter transformed to their corresponding numbers on a phone pad'''

    number_words_stripped = number_words.replace('-', '')
    return dash_number(dashless_words_to_number(number_words_stripped))


def dashless_words_to_number(number_words):
    '''takes a wordified phone number string without dashes and returns a string with
    all the letter transformed to their corresponding numbers on a phone pad'''
    return ''.join([letter_to_digit[x] for x in number_words])


def split_number(number):
    '''splits a US phone number string with dashes into two lists: one with
    the country and area code, the other containing the remaining segments'''

    if len(number) in [12, 14]:
        number_list = number.split('-')
        return number_list[:-2], number_list[-2:]

    else:
        raise Exception('invalid phone number, wrong length %d' % len(number))


def dash_number(number):
    '''add dashes to a US phone number string without dashes'''

    # start without 1
    if len(number) == 10:
        return '%s-%s-%s' % (number[:3], number[3:6], number[6:])

    # starts with 1
    elif len(number) == 11:
        return '%s-%s-%s-%s' % (number[0], number[1:4], number[4:7], number[7:])

    else:
        raise Exception('invalid phone number, wrong length %d' % len(number))


def read_word_dict(filename=None):
    '''takes a file containing a word per line and returns a dictionary
    mapping phone pad numbers to lists of words. words in file can be
    upper or lower case, and may only contain letters and digits. By default
    uses an english words dictionary.

    A mapping of digits to digits is also added to the dictionary'''

    if filename is None:
        filename = os.path.dirname(__file__)+'/english_words.txt'

    # include individual digits as words
    word_dict = {x: [x] for x in digit_to_digit}

    with open(filename, 'r') as f:
        for line in f.read().upper().split():
            key = dashless_words_to_number(line.replace('-', ''))

            if key in word_dict:
                word_dict[key].append(line)
            else:
                word_dict[key] = [line]

    return word_dict

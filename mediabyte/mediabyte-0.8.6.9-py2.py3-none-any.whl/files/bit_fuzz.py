import string
import random
from . import yota
from . import lib
#from .parse import omm


def bit_time_gen():
    """Returns YouTube time code format string generator."""
    while True:
        seconds_int = random.randint(0,9)
        seconds_str = str(seconds_int) + 's'
        minutes_int = random.randint(0,9)
        minutes_str = str(minutes_int) + 'm'
        hours_int = random.randint(0,9)
        hours_str = str(hours_int) + 'h'
        
        result_str = ""
        if hours_int:
            result_str += hours_str
        if minutes_int:
            result_str += minutes_str
        if seconds_int:
            result_str += seconds_str
        
        yield result_str


def bit_hash_char_gen():
    """Returns bit.ly hash format string generator."""

    letters_and_numbers = []
    for character in string.ascii_letters:
        letters_and_numbers.append(character)
    for i in range(10):
        letters_and_numbers.append(str(i))

    while True:
        result = ""
        for i in range(7):
            randInt = random.randint(0, len(letters_and_numbers)-1)
            character = letters_and_numbers[randInt]
            result += character
        yield result


def bit_title_gen():
    """Returns yota format title string generator."""

    letters_and_numbers = []
    for character in string.ascii_letters:
        letters_and_numbers.append(character)
    while True:
        title_length = random.randint(5, 16)
        result = ""
        
        randInt = random.randint(0, len(string.ascii_uppercase)-1)
        character = string.ascii_uppercase[randInt]
        result += character
        
        while len(result) < title_length:
            character_set = string.ascii_letters + string.digits + '_-#:!©™&"%&/()=?'
            randInt = random.randint(0, len(character_set) -1)
            character = character_set[randInt]
            if randInt % 4 == 0 and result != "":
                result += ' '
            result += character
        yield result


def bit_tag_gen():
    """Returns yota format tag string generator."""

    letters_and_numbers = []
    for character in string.ascii_letters:
        letters_and_numbers.append(character)
    while True:
        title_length = random.randint(3, 12)
        result = ""
        
        randInt = random.randint(0, len(string.ascii_lowercase)-1)
        character = string.ascii_lowercase[randInt]
        result += character
        
        while len(result) < title_length:
            
            character_set = string.ascii_lowercase + string.digits +  '_-+#:!&"%&/()?'                #+ _#:!©™=¤
            randInt = random.randint(0, len(character_set) -1)
            character = character_set[randInt]
            result += character
        yield result



def bit_gen():
    """Returns yota format Bit string generator."""
    
    while True:
        #myGen = yota
        my_title = next(bit_title_gen())
        #print(my_title)
        NoOfTimeCodes = random.randint(0,3)
        my_tags = []
        if NoOfTimeCodes > 0:
            my_tags.append('mp3')
        for i in range(random.randint(0,4)):
            my_tags.append(next(bit_tag_gen()))
        
        my_youtube_hash = next(bit_hash_char_gen())
        
        result = []
        result_strings = []
        
        for i in range(NoOfTimeCodes):
            my_time1 = next(bit_time_gen())
            my_time_1_int = lib.Convert._time_str(my_time1)
            result.append(my_time_1_int)
            result_strings.append(my_time1)

        if len(result_strings) == 2:
            # sort order lowest first
            if result[1] < result[0]:
                result = result_strings.reverse()

        final = 'b.' + my_youtube_hash
        # if time codes found
        if result_strings:
            final += '.' + result_strings[0]
        if my_title:
            final += '.' + my_title

        for item in my_tags:
            final += '.' + item
        if result_strings and len(result_strings) == 2:
            final += '.' + result_strings[1]

        yield final


def main(count, quiet=False, do_not_parse=False, mixtape=False):
    """ Takes count integer, returns yota Bit string list, 
        NB: expensive function, Bit object creation involved 
        which calls bitly.com to parse link."""

    myGen = bit_gen()
    result = []
    for i in range(count):
        myObjectStr = next(myGen)
        if not do_not_parse:
            try:
                myObject =  lib.Convert.omm(myObjectStr)
            except ValueError as e:
                return('Error:', myObjectStr, e)
            result.append(myObject.omm)
        else:
            result.append(myObjectStr)

    if not quiet:
        if not mixtape:
            return result
        # mixtape=True && quiet=False
        else:
            myMixtape = Mixtape( lib.Convert.omm(result[0]))
            for item in result[1:]:
                myMixtape +=  lib.Convert.omm(item)
            return myMixtape








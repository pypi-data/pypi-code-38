import string
import random
from . import yota
from .lib import Convert
#from .parse import omm


def youtube_hash_char_gen():
    """Returns YouTube hash format string generator."""

    letters_and_numbers = []
    for character in string.ascii_letters:
        #print(character)
        letters_and_numbers.append(character)
    for i in range(10):
        letters_and_numbers.append(str(i))
    for special_char in ['-','_']:
        letters_and_numbers.append(special_char)
    #return letters_and_numbers
    while True:
        result = ""
        for i in range(11):
            randInt = random.randint(0, len(letters_and_numbers)-1)
            character = letters_and_numbers[randInt]
            result += character
        yield result


def youtube_time_gen():
    """Returns random YouTube time code format string generator."""
    while True:
        seconds_int = random.randint(0,10)
        seconds_str = str(seconds_int) + 's'
        minutes_int = random.randint(0,10)
        minutes_str = str(minutes_int) + 'm'
        hours_int = random.randint(0,10)
        hours_str = str(hours_int) + 'h'
        
        result_str = ""
        if hours_int:
            result_str += hours_str
        if minutes_int:
            result_str += minutes_str
        if seconds_int:
            result_str += seconds_str
        
        yield result_str


# def bitly_hash_char_gen():
#     """Returns bit.ly hash format string generator."""

#     letters_and_numbers = []
#     for character in string.ascii_letters:
#         letters_and_numbers.append(character)
#     for i in range(10):
#         letters_and_numbers.append(str(i))

#     while True:
#         result = ""
#         for i in range(7):
#             randInt = random.randint(0, len(letters_and_numbers)-1)
#             character = letters_and_numbers[randInt]
#             result += character
#         yield result


def yota_title_gen():
    """Returns yota title format string generator."""

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


def yota_tag_gen():
    """Returns yota tag format string generator."""

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



def yota_gen():
    """Returns yota format string generator."""
    
    while True:
        #myGen = yota
        my_title = next(yota_title_gen())
        #print(my_title)
        my_tags = []
        for i in range(random.randint(0,4)):
            my_tags.append(next(yota_tag_gen()))
        
        my_youtube_hash = next(youtube_hash_char_gen())
        NoOfTimeCodes = random.randint(0,3)
        result = []
        result_strings = []
        for i in range(NoOfTimeCodes):
            my_time1 = next(youtube_time_gen())
            my_time_1_int = Convert._time_str(my_time1)
            result.append(my_time_1_int)
            result_strings.append(my_time1)

        if len(result_strings) == 2:
            # sort order lowest first
            if result[1] < result[0]:
                result = result_strings.reverse()

        final = 'y.' + my_youtube_hash
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
    """Takes count integer, returns count yota strings."""
    myGen = yota_gen()
    result = []
    for i in range(count):
        myObjectStr = next(myGen)
        if not do_not_parse:
            myObject =  Convert.omm(myObjectStr)
            result.append(myObject.omm)
        else:
            result.append(myObjectStr)

    if not quiet:
        if not mixtape:
            return result
        # mixtape=True && quiet=False
        else:
            myMixtape = yota.Mixtape(Convert.omm(result[0]))
            for item in result[1:]:
                myMixtape +=  Convert.omm(item)
            return myMixtape








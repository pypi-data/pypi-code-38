from . import bit
import re


"""
                    yNo Bit String Parser
                       March 10th 2019
                        by d@v1d.dk

What's New: porting from yno.py

"""


def get_time_codes(tag_str):

    """Extract YouTube time codes from CLI string."""

    mylist = tag_str.split(".")
    mytimes = []
    newtimes = []
    for item in mylist:

        yt_time_match = re.search(r'^(\d{1,2}[hms]){1,3}$', item)
        if yt_time_match:
            #print('time code match:', yt_time_match.group(0))
            mytimes.append(yt_time_match.group(0))
        else:
            newtimes.append(item)
#    print('time:', mytimes, ".".join(newtimes))
    return(mytimes, ".".join(newtimes))


def get_titles(tag_str):

    """Extract titles from CLI string."""

    mylist = tag_str.split(".")
    mytitles = []
    newtitles = []
    for i, item in enumerate(mylist):
        title_match = re.search('^[A-Z]', item)  # match on uppercase first character
        if title_match:
            # check not matching bitly hash
            if i != 1:
                mytitles.append(item)
            else:
                newtitles.append(item)
        else:
            newtitles.append(item)
    #if len(mytitles) == 0:
    #    mytitles = ['MyBit']
    return(mytitles, ".".join(newtitles))


def get_bitly_hash(tag_str):

    """Extract Bitly URL or hash from string."""

    mylist = tag_str.split(".")

    newtimes = []
    result = ""

    if mylist[0] == 'b':
        #print(tag_str)
        #print('get_bitly_hash_result:', mylist[1], 'rest:', ".".join(mylist[2:]))
        return(mylist[1], ".".join(mylist[2:]))
        #m = re.search('b\.([^\.]+)\.?(.+$)', tag_str)
        #print('Bit object matched...')
        #print(tag_str[2:9])
        #print(tag_str[10:])
        #return(tag_str[2:9], tag_str[10:])
        print(m.group(1), m.group(2))
        return(m.group(1), m.group(2))


def parse_element_types(str_input):
    """Parse string for time codes, titles and URL."""
    bitly_hash, rest = get_bitly_hash(str_input)
    time_codes, rest2 = get_time_codes(rest)
    titles, rest3 = get_titles(rest2)
    
    raw_tags = rest3.split(".")
    tags = []
    for item in raw_tags:
        if len(item) > 0:
            tags.append(item)

    #print('tags:',tags)

    return(time_codes, titles, bitly_hash, tags)


def print_report(result_in):
    """Print time code, title, url and tags."""
    if result_in[0]:
        print("Time Codes: " + " ".join(result_in[0][:]))
    if result_in[1]:
        print("Titles: " + " ".join(result_in[1]))
    if result_in[2]:
        print("YouTube URL: " + result_in[2])
    if result_in[3]:
        print("Tags: " + " ".join(result_in[3]))



def main(yno_string):
    """Main function, takes a yNo format string, returns string result."""
    result = parse_element_types(yno_string)
    resObj = build_bit_object(result)
    return resObj


def build_bit_object(result_list):
    """Builds and returns Bit object."""
    times_list = result_list[0]
    title_list = result_list[1]
    bitly_hash = result_list[2]
    tags_list = result_list[3]

    if len(title_list) == 0:
        #title = 'MyBit'
        title = None
    else:
        title = result_list[1][0]

    # Sample detected (two time codes)
    if len(times_list) == 2 and 'mp3' in tags_list:

        timesinsec_list = []
        for item in times_list:
            timesinsec_list.append(time_str(item))

        try:
            newBitMp3 = bit.Mp3(bitly_hash, title=title, time_start=timesinsec_list[0], time_end=timesinsec_list[1], tags=tags_list)
            return newBitMp3
        except:
            raise ValueError("Building BitMp3 object failed (exactly two time codes needed")

    elif len(times_list) == 1 and 'mp3' in tags_list:

        timesinsec_list = []
        #for item in times_list[]:
        timesinsec_list.append(time_str(times_list[0]))

        try:
            newBitMp3 = bit.Mp3(bitly_hash, title=title, time_start=timesinsec_list[0], tags=tags_list)
            return newBitMp3
        except:
            raise ValueError("Building BitMp3 object failed (exactly two time codes needed")

    
    elif times_list and not 'mp3' in tags_list:
        raise ValueError('Time code matched but content type not indicated (presently mp3 only)')


    elif 'mp3' in tags_list:
        try:
            newBitMp3 = bit.Mp3(bitly_hash, title=title, tags=tags_list)
            return newBitMp3
        except:
            raise ValueError("Building BitMp3 object failed (no time codes)")


    elif len(times_list) == 0:

        try:
            #print('result_list[1][0]:', result_list[1][0])
            #print('bitly_hash:', bitly_hash, 'title:', title, 'tags:', tags_list)
            newBitMp3 = bit.Link(bitly_hash, title=title, tags=tags_list)
            return newBitMp3
        except:
            raise ValueError("Building Bit object failed")

        

def mp3_or_not(str_in_question):
    """Test if first tag is 'mp3'."""
    #tags = parse_element_types(str_in_question)[3]
    m = re.search('\.mp3', str_in_question)
    if m:
    #if tags[0] == 'mp3':
        return(True)


# def main(bno_str):

#     # MP3 tag found
#     if mp3_or_not(bno_str):
#         #print('.mp3 matched')
#         BitMp3 = go(bno_str)
#         #BitMp3 = build_bit_object(result)

#     else:
#         Bit = go(bno_str)
#         BitMp3 = Bit
#         #print(result)
#         #BitMp3 = Bit.Bit(result)

#     return(BitMp3)


# def youtube_time_format(seconds):
#     """Takes time in seconds, returns YouTube format time code."""

#     hours = int(seconds / 3600)
#     seconds = seconds - (hours * 3600)
#     minutes = int(seconds / 60)
#     rest = seconds - minutes * 60
#     final_str = ''
#     if hours:
#         final_str += str(hours) + 'h'
#     if minutes:
#         final_str += str(minutes) + 'm'
#     if seconds:
#         final_str += str(rest) + 's'

#     return(final_str)


def time_str(time_str):
        """Takes '2h5m3s' format time string, returns value in seconds (internal method)."""

        m = re.search('([0-9]+)s', time_str)   # match seconds
        m2 = re.search('([0-9]+)m', time_str)  # match minutes
        m3 = re.search('([0-9]+)h', time_str)  # match hours

        if m:
            seconds = m.group(1)
        else: seconds = 0

        if m2:
            minutes = m2.group(1)
        else: minutes = 0

        if m3:
            hours = m3.group(1)
        else: hours = 0

        seconds_total = int(seconds) + (int(minutes) * 60) + (int(hours) * 3600)

        return(seconds_total)

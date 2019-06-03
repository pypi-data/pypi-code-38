"""yNo Sample String Parser (Yota implementation)."""
import re


"""
                yNo Sample String Parser 2.2
                       March 5th 2019
                        by d@v1d.dk
What's New: Fix 11-character tag bug
"""


def get_time_codes(tag_str):

    """Extract YouTube time codes from CLI string."""

    mylist = tag_str.split(".")
   ##print('mylist in get_time_codes():', str(mylist))
    mytimes = []
    newtimes = []
    for item in mylist:

        yt_time_match = re.search(r'^(\d+[hms]){1,3}$', item)
        if yt_time_match:
            mytimes.append(yt_time_match.group(0))
        else:
            newtimes.append(item)
   ##print('mytimes:', mytimes, 'newtimes: ', ".".join(newtimes))
    return(mytimes, ".".join(newtimes))


def get_titles(tag_str):

    """Extract titles from CLI string."""

    #print('tag_str:', tag_str)
    mylist = tag_str.split(".")
   ##print('tag_str at start of get_titles: ', tag_str)
    #print('mylist at start of get_titles: ', mylist)
    mytitles = []
    newtitles = []
    for i, item in enumerate(mylist):
        title_match = re.search('^[A-Z]', item)  # match on uppercase first character
        if title_match:
            #if len(item) != 11: #NB - very hacky solution, uses string length
            mytitles.append(item)
            for item in mylist[i+1:]:
                newtitles.append(item)
                #print('item:', item)
                #print('mytitles:', mytitles)
                #print('newtitles:', newtitles)
            return(mytitles, ".".join(newtitles))
        else:
            newtitles.append(item)
        # else:
        #     newtitles.append(item)
    return(mytitles, ".".join(newtitles))


def get_youtube_url(tag_str):

    """Extract YouTube URL or hash from string."""

    mylist = tag_str.split(".")

    newtimes = []
    result = ""


    for item in mylist:

        http_match = re.search('^http', item)  # match on starts with http
        yt_url_match = re.search('^youtube.com/watch?v=([a-zA-Z0-9-]{11})', item)
        # match on starts with 'youtube.com/'
        yt_url_match_2 = re.search('^youtu.be/', item)     # match on starts with 'youtu.be/'
        yt_hash_match = re.search('^[a-zA-Z0-9\-\_]{11}$', item)  # match on YouTube hash format

        if http_match:

            result = item
        elif yt_url_match:
            youtube_hash = item
            result = item
        elif yt_url_match_2:

            result = item
        elif yt_hash_match:
            youtube_hash = yt_hash_match.group(0)
            result = youtube_hash
            # NB: Possibly hacky, not sure
            if tag_str[:2] == 'y.':
                newtimes.append(tag_str[13:])
            else:
                newtimes.append(tag_str[11:]) 
            
            return(result, ".".join(newtimes[1:])[1:])

        else:
            newtimes.append(item)
    if not result:
        raise ValueError("No YouTube hash match found")

    return(result, ".".join(newtimes)[1:])


def get_bit_object(input_str):

    m = re.search('\.b\.', input_str)
    if m:
        bit_object_results = input_str.split('.b.')
    else:
        bit_object_results = [input_str]
    new_objects = []
    for item in bit_object_results:
        new_objects.append(item)

    if len(new_objects) > 1:
        leading_str = new_objects[0]
    else:
        return([], input_str)

    result = ""
    result_list = []
    
    for item in bit_object_results[1:]:

        result = 'b.' + item
        result_list.append(result)

    return(result_list, leading_str)


def parse_element_types(str_input):
    """Parse string for time codes, titles and URL."""
    bit_object_list, rest0 = get_bit_object(str_input)
   ##print('rest0 after get_bit_objects:', rest0)
   ##print('bit_object_list:', bit_object_list)
    yt_url, rest1 = get_youtube_url(rest0)
   ##print('rest1 after get_youtube_url:', rest1)
    time_codes, rest2 = get_time_codes(rest1)
   ##print('rest2 after get_time_codes:', rest2)
    titles, rest3 = get_titles(rest2)
   ##print('rest3 after get_titles:', rest3)
    
    if rest3:
        tags = rest3.split(".")
    else:
        tags = []
   ##print('tags after split: ',tags)
    #print('rest3:', rest3)

    return(time_codes, titles, yt_url, tags, bit_object_list)


def print_report(result_in):
    """Print data fields."""
    
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
    return result


# def build_yota_object(result_list):
#     """Builds and returns Yota object."""
#     times_list = result_list[0]
#     yturl_str = result_list[2]
#     tags_list = result_list[3]

#     if len(times_list) == 2:

#         timesinsec_list = []
#         for time in times_list:
#             seconds_match = re.search(r'(\d{1,2})s', time)
#             if seconds_match:
#                 secs = int(seconds_match.group(1))
#             else:
#                 secs = 0
#             minutes_match = re.search(r'(\d{1,2})m', time)
#             if minutes_match:
#                 minutes = int(minutes_match.group(1))
#             else: minutes = 0
#             hour_match = re.search(r'(\d{1,2})h', time)
#             if hour_match:
#                 hours = int(hour_match.group(1))
#             else: hours = 0

#             total_secs = secs + 60*minutes + 3600*hours

#             timesinsec_list.append(total_secs)




#         try:
#             new_sample = Sample(url=yturl_str, title=" ".join(result_list[1]), \
#             time_start=timesinsec_list[0], time_end=timesinsec_list[1], tags=tags_list)
#             return new_sample
#         except:
#             raise ValueError("Exactly two time codes needed")
    
    
#     elif len(times_list) == 1:

#         timesinsec_list = []
#         for time in times_list:
#             seconds_match = re.search(r'(\d{1,2})s', time)
#             if seconds_match:
#                 secs = int(seconds_match.group(1))
#             else:
#                 secs = 0
#             minutes_match = re.search(r'(\d{1,2})m', time)
#             if minutes_match:
#                 minutes = int(minutes_match.group(1))
#             else: minutes = 0
#             hour_match = re.search(r'(\d{1,2})h', time)
#             if hour_match:
#                 hours = int(hour_match.group(1))
#             else: hours = 0

#             total_secs = secs + 60*minutes + 3600*hours

#             timesinsec_list.append(total_secs)




#         try:
#             new_cue = Cue(yt_hash=result_list[2], title=" ".join(result_list[1]), \
#             time_start=timesinsec_list[0][0], tags=tags_list)
#             return new_cue
#         except:
#             raise ValueError("Exactly one time codes needed")
        

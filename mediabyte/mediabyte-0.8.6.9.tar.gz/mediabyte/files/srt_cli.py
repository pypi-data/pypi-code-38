#!/home/dd/anaconda3/bin/python
#      srt_cli.py v0.2 February 26th 2019
# - get links to keyword occurrences in YouTube 
#   video from the auto-generated subtitles
# - demonstration of interacting with
#   the yota module in practice

from yota import yNo
import sys

## SETUP ## 
# ARGUMENT HANDLING
try: # check for mandatory youtube URL argument
    youtube_url_from_arg = sys.argv[1]
except:
    exit('Error: no youtube URL argument found')
try: # check for mandatory search term argument
    search_term_from_arg = sys.argv[2]
except:
    exit('Error: no search term argument found')
try: # check if optional clip length argument was passed
    clip_length_from_arg = int(sys.argv[3])
except:
    # or default to clip length 10 seconds
    clip_length_from_arg = 10

## MAIN ##
# CREATE YOTA OBJECT
myYota = yNo(youtube_url_from_arg)
# SEARCH SUBTITLES .SRT
srt_search_results = myYota.srt_search(search_term_from_arg, clip_length=clip_length_from_arg)

## OUTPUT ##
# PRINT RESULT
for item in srt_search_results:
    print(item.url)
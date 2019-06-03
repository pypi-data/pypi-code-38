#!/home/dd/anaconda3/bin/python

# takes YouTube URL, matching .srt filename and search term(s),
# returns time code YouTube URLs of occurrences

import re, sys
from datetime import timedelta


def main(srt_file, search_term):
    """Takes .srt filename and search term, 
    returns YouTube time code URLs of occurrences."""

    f = open(srt_file,'r')
    content = f.readlines()
    f.close()
    
    new_content = []
    for line in content:
        newline = re.sub('<.+?>','', line)
        new_content.append(newline)

    def run_ad_time_parser():
        """Search a .srt file for time codes associated with search term."""
        result_list = []
        for i, line in enumerate(new_content):
            m = re.search(search_term, line)
            if m:
                result_list.append(new_content[i-1])

        return(result_list)

    result_list = run_ad_time_parser()

    def convert_time(time_str):
        m = re.search('^(\d\d):(\d\d):(\d\d)', time_str)
        try:
            hours = m.group(1)
        except:
            hours = 0
        try:
            minutes = m.group(2)
        except:
            minutes = 0
        try:
            seconds = m.group(3)
        except:
            seconds = 0
        
        
        # correct time code 2 seconds back
        current_time = timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds))
        subtraction_time = timedelta(seconds=2)
        if subtraction_time < current_time:
            #print('current_time:', current_time)
            corrected_time = current_time - subtraction_time
        # in case of 0 or 1 seconds
        else:
            #print('correcting:', current_time)
            corrected_time = timedelta(seconds=1)  # NB: start from 1s minimum
        
        time_str = str(corrected_time)
        m = re.search('(\d{1,2}):(\d\d):(\d\d)', time_str)
        hours = m.group(1)
        minutes = m.group(2)
        seconds = m.group(3)

        return(hours, minutes, seconds)

    result_matrix = []
    for line in result_list:
        result_matrix.append(convert_time(line))

    try:
        m = re.search('\-([a-zA-Z0-9\-\_]{11})\.', srt_file)
        if m:
            base_url = 'https://www.youtube.com/watch?v=' + m.group(1)
    except ValueError:
            print('No YouTube hash matched in filename')

    urls_with_time_codes = []
    for tup in result_matrix:
        if int(tup[0]) > 0: # hours present
            new_url = base_url + '&t=' + str(tup[0]) + 'h'
        else:
            new_url = base_url + '&t='
        if int(tup[1]) > 0: # minutes present           
            new_url = new_url + str(tup[1]) + 'm'
        if int(tup[2]) > 0: # seconds present
            new_url = new_url + str(tup[2]) + 's'
            urls_with_time_codes.append(new_url)
    uniqued_results = []
    for item in urls_with_time_codes:
        if not item in uniqued_results:
            uniqued_results.append(item)
    return (uniqued_results[1:])  # NB: Very hacky, throwing away first faulty result

if __name__ == '__main__':

    result = main(sys.argv[1], sys.argv[2])
    for item in result:
        print(item)

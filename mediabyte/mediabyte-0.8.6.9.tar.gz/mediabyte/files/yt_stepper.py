#!/home/dd/anaconda3/bin/python
import re

def next_page(url):
    
    """Takes YouTube search page URL, returns next page URL."""
    
    search_terms = re.search('query=(.*?)(&|$)', url)
    first_url = 'https://www.youtube.com/results?search_query=grey+hats'
    second_url = 'https://www.youtube.com/results?search_query=grey+hats&page=2'
    
    check_for_page_no = re.search('&page=', url)
    if check_for_page_no:
        m = re.search('page=(\d{1,2})', url)
        page_no = m.group(1)
        new_page_no = str(int(page_no) + 1)
        new_url = url.replace('page=' + page_no, 'page=' + new_page_no)
    else:
        new_url = second_url.replace('grey+hats',search_terms.group(1))
        
    return(new_url)
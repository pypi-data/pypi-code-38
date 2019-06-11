import os
import re
import time
import threading
from typing import Union, List, Tuple

from urllib.parse import quote, unquote
import urllib.request as req  # built-in for Python 3
from urllib.error import HTTPError

from bs4 import BeautifulSoup  # pip/beautifulsoup4

# May require update in the future
_USER_AGENT_HEADER = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36'
_LIST_OF_ALL_TYPES = ['tw', 'jr', 'twes', 'cn', 'jp', 'jpjr', 'kr', 'krjr', 'ph', 'th', 'hk', 'hkes']


def _init_header(verbose: bool = False) -> None:
    global FLAG_header_inited
    if 'FLAG_header_inited' not in globals():
        if verbose: print(f'using fake user-agent header: {_USER_AGENT_HEADER}')
        opener=req.build_opener()
        opener.addheaders=[('User-Agent', _USER_AGENT_HEADER)]
        req.install_opener(opener)
        FLAG_header_inited = True
    return
    

def _find_last_index(url_prefix: str, verbose: bool = False) -> int:
    _init_header(verbose=verbose)
    pat = re.compile(r'class=\"lazyload img-fluid\"')

    # find the last index number
    current_index = 1
    for step in [1000, 100, 10, 1]:
        if current_index == -1:
            break
        for i in range(current_index, current_index+step*10, step):
            url = f'{url_prefix}{i}'
            if verbose: print(f'Opening URL: {url}')
            response = req.urlopen(url).read().decode('utf8')
            if not re.search(pat, response):
                if i == 1:
                    current_index = -1 # not found
                else:
                    current_index = i - step
                break
    return current_index

def _download_img(source: str, destination: str, progress: Tuple[int, int] = (0,0), verbose: bool = False) -> None:
    """
    Download a single image.
    """
    if verbose: print(f'({progress[0]}/{progress[1]}) Downloading: {source} --> {destination}')
    
    for retry_count in range(1, 6):
        try:
            req.urlretrieve(source, destination)
        except HTTPError:
            print(f'({progress[0]}/{progress[1]}) Connection error. Wait for 10 seconds and retry({retry_count}/5)...')
            time.sleep(10)
        else:
            break
    else:  # this block will be executed if the for-loop is not "break"ed
        print('Retry limit reached. This image will be ignored.')
    return

def fetch_by_url(url: str, num_of_parallel_downloads: int = 10, verbose: bool = True) -> None:
    """
    Download pictures tagged as the same school according to the specified URL.
    """
    match_results = re.findall(r'https?:\/\/uniform\.wingzero\.tw\/school\/(intro|album)\/([a-z]+)\/([0-9]+)([\/][0-9]+)?', url)
    
    if match_results is None:
        print('\nSorry. This URL is not supported.\nValid URL for this application should be like: http://uniform.wingzero.tw/school/album/twes/78\n')
        raise ValueError('URL not supported')
    if num_of_parallel_downloads < 1:
        raise ValueError('num_of_parallel_downloads should be > 1')
    
    
    school_type: str = match_results[0][1]
    school_id: int = int(match_results[0][2])
    url_prefix = f'http://uniform.wingzero.tw/school/album/{school_type}/{school_id}'
    
    _init_header(verbose=verbose)
    
    img_urls = []
    # Fetch page content
    for page_index in range(1, 10):
        if verbose: print(f'Opening {url_prefix}/{page_index}...')
        try:
            response = req.urlopen(f'{url_prefix}/{page_index}').read()
        except HTTPError as ex:
            print('An error happened when trying to read the webpage.\nThis is probably caused by network issue, or the "fake user-agent header" needs update.')
            raise HTTPError(ex)
        
        # Analyze the page with BeautifulSoup
        soup = BeautifulSoup(response, 'lxml')
        
        if page_index == 1:
            school_name = soup.find('h1', class_='h1_title').find(text=True, recursive=False).strip()
        
        img_elements = soup.find_all('img', class_='lazyload img-fluid')
        if len(img_elements) == 0:
            if verbose: print(f'No image found on {url_prefix}/{page_index}. \nStop fetching pages.')
            break
        img_urls.extend([e['data-src'] for e in img_elements])


    # Download images
    output_folder_name = f'{school_type}{school_id:04d}_{school_name}'
    
    if not os.path.isdir(output_folder_name):
        os.makedirs(output_folder_name, exist_ok=True)
    output_path = os.path.abspath(output_folder_name)
        
    for img_index, source in enumerate(img_urls):
        destination = output_path + '/' + source.split('/')[-1]  # use / instead of \\ for Windows+Linux compatibility
        while threading.active_count() >= num_of_parallel_downloads:
            time.sleep(0.1)
        threading.Thread( target=_download_img, args=(source, destination, (img_index+1, len(img_urls)), verbose) ).start()
    return
    

def fetch_all(school_types: Union[str, List[str]]=_LIST_OF_ALL_TYPES, num_of_parallel_downloads: int = 10, verbose: bool = True) -> None:
    _init_header(verbose=verbose)
    if type(school_types) is str:
        school_types = [school_types]
    
    for school_type in school_types:
        last_index_number = _find_last_index(f'http://uniform.wingzero.tw/school/album/{school_type}/')
        if verbose: print(f'Last index number for school type "{school_type}" is {last_index_number}.')
        
        for school_index in range(1, last_index_number+1):
            fetch_by_url(f'http://uniform.wingzero.tw/school/album/{school_type}/{school_index}', num_of_parallel_downloads=num_of_parallel_downloads, verbose=verbose)
        
    return
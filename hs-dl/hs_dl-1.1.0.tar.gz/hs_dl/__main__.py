'''hs_dl

Simple HorribleSubs Anime Downloader

Usage:
    hs_dl [(-q <quality>)] [options] (<anime_link>)

Options:
   -v            Verbose Output
   -n            Dry Run
   -q <quality>  Quality to download [default: 1080]
   -h, --help    Show this page

Arguments:
    <quality>:      1080
                    720
                    480
    <anime_link>:   Link to horriblesubs. If link contains special characters
                    like #, then it is recommended to put link in single quotes.
'''

from docopt import docopt
import re
from hs_dl import HorribleDownloader

if __name__ == '__main__':

    arguments = docopt(__doc__)
    quality = arguments['-q']
    verbose = arguments['-v']
    dry_run = arguments['-n']
    url = arguments['<anime_link>']

    if verbose:
        print(arguments)

    if quality not in ['1080', '720', '480', None]:
        print("\n\n[~] Quality argument is incorrect. See documentation\n")
        print(__doc__)
        exit()

    url_regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    is_url = re.match(url_regex, url)

    if is_url is None:
        print(f'{url} provided is invalid!')
        exit()

    hs_downloader = HorribleDownloader(url = url, 
                                        quality = quality, 
                                        verbose = verbose,
                                        dry_run = dry_run)
    hs_downloader.run()
    

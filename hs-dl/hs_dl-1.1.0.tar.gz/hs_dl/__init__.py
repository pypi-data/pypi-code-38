from multiprocessing.pool import ThreadPool as Pool
import os
import re
import requests
from requests_html import HTMLSession
import tempfile
from time import sleep
from urllib.parse import urlencode


class HorribleDownloader:
    def __init__(self, url, quality, verbose, dry_run):
        self.url = url
        self.quality = quality
        self.verbose = verbose
        self.dry_run = dry_run
        self.temp_dir = tempfile.TemporaryDirectory(dir='/var/tmp')
        self.api_url = 'https://horriblesubs.info/api.php?'
        self.torrent_links = []
        self.workers = 8


    def download_torrent(self, link):
        tries = 3
        while tries > 0:
            if self.dry_run:
               print(f"[ ] Would Download {link['torrent_file_name']} at {link['torrent_file_path']}]") 
               return
            res = requests.get(link['torrent_link'])
            if res.status_code != 200:
                tries -= 1
                if self.verbose:
                    print(f"[~] Got status code: {res.status_code} for {link['torrent_file_name']}")
                '''
                getting 429 http status code on multiple requests
                that's why sleep for 1 second since api doesn't
                provide any sleep_till header in response
                '''
                sleep(1)
                continue
            with open(link['torrent_file_path'], 'wb') as f:
                f.write(res.content)
                print(f"[+] Downloaded {link['torrent_file_path']}")
                return
        print(f"[-] Couldn't Download {link['torrent_file_path']}")
   

    def download_torrents(self):
        session = HTMLSession()
        response = session.get(self.url)

        # Find show_id which is unique for each show
        try:
            show_id = response.html.find('script', containing='hs_showid', first=True)
            show_id = int(re.findall(r'\d+', show_id.text)[0])
        except Exception as e:
            print(e)
            return -1

        # next_id is defined beacuse of pagination
        next_id = 0
        
        print('[ ] Collecting Torrent Info...')
        while True:

            query_params = {
                'method': 'getshows',
                'type': 'show',
                'showid': show_id,
                'nextid': next_id
            }

            query_string = urlencode(query_params)
            torrent_url = self.api_url + query_string

            if self.verbose:
                print(f'[*] Acting on {torrent_url}')
            else:
                print(f'[ ] Accessing page {next_id}')

            response = session.get(torrent_url)

            if response.status_code == 200 or response.status_code < 300:
                if self.verbose: 
                    print(f"[*] Got html page for show id {show_id} and page {next_id}")
            else:
                print('[~] Status Code for {torrent_url}: {response.status_code}')
                return

            if response.text == 'DONE':
                print('[ ] Done Accessing pages')
                break

            episode_elements = response.html.find('.rls-info-container')
            for episode_element in episode_elements:
                #print(episode_element.find('.rls-label', first=True).text)
                try:
                    links_container = episode_element.find('.rls-links-container', first=True)
                    link_container = links_container.find('.rls-link', containing=self.quality, first=True) 
                    torrent_file_name = link_container.attrs['id'] + '.torrent'
                    torrent_file_path = os.path.join(self.temp_dir.name, torrent_file_name)
                    torrent_link = link_container.find('.hs-torrent-link', first=True).find('a', first=True).attrs['href']

                    torrent_info = {
                        'torrent_link': torrent_link,
                        'torrent_file_name': torrent_file_name,
                        'torrent_file_path': torrent_file_path
                    }

                    self.torrent_links.append(torrent_info)

                except Exception as e:
                    print(e)

            next_id += 1

        if self.dry_run:
            print('\n[ ] Starting Emulation of Downloading')
        else:
            print('\n[ ] Starting Downloading')
        print('[ ] NOTE: Downloaded files may appear out of order.')

        # create thread pool
        pool = Pool(self.workers)
        for result in pool.map(self.download_torrent, self.torrent_links):
            pass

        if self.dry_run:
            print('[ ] Finished Emulation of Downloading')
        else:
            print('[ ] Finished Downloading')


    def run(self):
        self.download_torrents()
        if not self.dry_run:
            input("Quit?")


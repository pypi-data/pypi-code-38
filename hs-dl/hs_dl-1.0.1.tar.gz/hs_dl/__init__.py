import os
import re
import requests
from requests_html import HTMLSession
import tempfile


class HorribleDownloader:
    def __init__(self, url, quality, verbose, dry_run):
        self.url = url
        self.quality = quality
        self.verbose = verbose
        self.dry_run = dry_run
        self.temp_dir = tempfile.TemporaryDirectory(dir='/var/tmp')

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
        while True:
            torrent_url = 'https://horriblesubs.info/api.php?method=getshows&type=show&showid={}&nextid={}'.format(show_id, next_id)
            response = session.get(torrent_url)

            if response.status_code == 200 or response.status_code < 300:
                if self.verbose: 
                    print(f"[*] Got html page for show id {show_id} and page {next_id}")
            else:
                print('[~] Status Code for {torrent_url}: {response.status_code}')
                return

            if response.text == 'DONE':
                print('[+]', response.text)
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

                    res = requests.get(torrent_link)
                    if self.dry_run:
                       print(f'[*] Would Download {torrent_file_name} at {torrent_file_path}]') 
                    else:
                        with open(torrent_file_path, 'wb') as f:
                            f.write(res.content)
                            print(f'[+] Downloaded {torrent_file_path}')

                except Exception as e:
                    print(e)

            next_id += 1

    def run(self):
        self.download_torrents()
        if not self.dry_run:
            input("Quit?")


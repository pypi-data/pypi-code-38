import requests
import webbrowser
import json
import sys, os

base_url = 'https://yts.lt/api/v2/list_movies.json'
while(True):
    movie = input('Enter movie name: ')
    movie = movie.replace(' ','%20')
    data_json = (requests.get(base_url + '?query_term={}'.format(movie)).json())
    print('Title: ' + data_json['data']['movies'][0]['title_long'])
    print('Description: ' + data_json['data']['movies'][0]['description_full'])
    q = input('Do you want to watch the trailer : [Y/N]')
    if(q=='Y' or q=='y'):
        webbrowser.open('https://www.youtube.com/watch?v={}'.format(data_json['data']['movies'][0]['yt_trailer_code']))
        sys.stdout = open(os.devnull, 'w')
        input()
        sys.stdout = sys.__stdout__
    else:
        pass
    qu = input('Do you want to download the torrent file : [Y/N]')
    if(qu=='Y' or qu=='y'):
        torrent = requests.get(data_json['data']['movies'][0]['torrents'][0]['url'])
        with open('{}.torrent'.format(data_json['data']['movies'][0]['title_long']), 'wb') as f:
            f.write(torrent.content)
        print('Torrent file will be downloaded to the current working directory : {} \n You\'ll need a bit torrent client application to download the files.format(os.getcwd()))
    else:
        pass

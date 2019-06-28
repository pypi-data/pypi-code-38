
import deezer as deezer
import requests, json, os

localdir = os.getcwd()
headers = {'content-type': 'application/json',
               'Authorization': 'Token bb1131f893f91f1bf5461285b26c0b622d21a37e'}
def crawl_auto(gmail, password, arl, sv, ip, output):
    dez = deezer.Login(gmail, password, arl)
    tracks = requests.get("http://54.39.49.17:8031/api/tracks/?status=0&sv={}".format(sv)).json()['results']
    for track in tracks:
        print("Update Status audio: " + str(track['deezer_id']) + " - " + track['title'] + " - " + track['artist'])
        track['status'] = True
        try:
            requests.put("http://54.39.49.17:8031/api/tracks/{}/".format(track['id']),
                         data=json.dumps(track), headers=headers)
        except:
            requests.put("http://54.39.49.17:8031/api/tracks/{}/".format(track['id']),
                         data=json.dumps(track), headers=headers)
            pass

    for track in tracks:
        try:
            print("crawl audio: " + str(track['deezer_id']) + " - " + track['title'] + " - " + track['artist'])
            track['status'] = True
            track = dez.download(track['deezer_id'], track,ip, output)
            if (os.path.exists(track['url_128'])):
                track['error_code'] = 0
            else:
                track['error_code'] = 1
            try:
                requests.put("http://54.39.49.17:8031/api/tracks/{}/".format(track['id']),
                             data=json.dumps(track), headers=headers)
            except:
                requests.put("http://54.39.49.17:8031/api/tracks/{}/".format(track['id']),
                             data=json.dumps(track), headers=headers)
                pass
        except Exception as e:
            print("error Download:" + str(e))
            pass
def find_audio(deezer_id):
    tracks = requests.get("http://54.39.49.17:8031/api/tracks/?deezer_id={}".format(deezer_id)).json()['results']
    return tracks
def get_info(deezer_id,ip,output,quality):
    dez = deezer.Login("mun87081@cndps.com", "asd123a@", "6afe8dd1218df2ae7927210aeca25ef17bc46920072ea72ddf16225eeabf79637d84b43e37f0e2f0c0a6a280d60d5516223e7c4f3270f6a32e8062e4832fb2e6f9c66b8c2f4072f9845061dd3b0ce45e9d5c981b4c8537be3fbf9fd609b14e56")
    track={}
    track_j=requests.get("https://api.deezer.com/track/"+deezer_id).json()
    track['deezer_id']=track_j['id']
    track['title']=track_j['title'][:255]
    track['title_short'] = track_j['title_short'][:255]
    track['isrc'] =  track_j['isrc']
    track['duration'] = track_j['duration']
    track['rank'] = track_j['rank']
    track['explicit_lyrics'] = track_j['explicit_lyrics']
    track['status']=1
    track['artist']= track_j['artist']['name']
    track = dez.download(track['deezer_id'], track, ip, output,quality)
    track['error_code'] = 0
    track['status'] = 1
    try:
        requests.post("http://54.39.49.17:8031/api/tracks/",
                     data=json.dumps(track), headers=headers)
    except:
        requests.post("http://54.39.49.17:8031/api/tracks/",
                      data=json.dumps(track), headers=headers)
    return track

def get_audio(deezer_id,ip,output,quality):
    tracks = find_audio(deezer_id)
    if len(tracks) == 0:
        print(json.dumps(get_info(deezer_id, ip, output,quality)))
    else:
        track = tracks[0]
        if track['url_128'] == None:
            dez = deezer.Login("mun87081@cndps.com", "asd123a@",
                               "6afe8dd1218df2ae7927210aeca25ef17bc46920072ea72ddf16225eeabf79637d84b43e37f0e2f0c0a6a280d60d5516223e7c4f3270f6a32e8062e4832fb2e6f9c66b8c2f4072f9845061dd3b0ce45e9d5c981b4c8537be3fbf9fd609b14e56")
            track = dez.download(track['deezer_id'], track, ip, output,quality)
            track['error_code'] = 0
            track['status'] = 1
            try:
                requests.put("http://54.39.49.17:8031/api/tracks/{}/".format(track['id']),
                             data=json.dumps(track), headers=headers)
            except:
                requests.put("http://54.39.49.17:8031/api/tracks/{}/".format(track['id']),
                             data=json.dumps(track), headers=headers)
        print(json.dumps(track))






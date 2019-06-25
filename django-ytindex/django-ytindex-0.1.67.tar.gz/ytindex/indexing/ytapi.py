import os
import googleapiclient.discovery
import googleapiclient.errors

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

class Youtube():
  def __init__(self, key):
    api_service_name = "youtube"
    api_version = "v3"
    self.__yt = googleapiclient.discovery.build(api_service_name, api_version, developerKey=key)

  def listplaylist(self, id):
    r = self.__yt.playlistItems().list(part='contentDetails',playlistId=id, maxResults=50).execute()
    for result in r.get('items', []):
      yield result['contentDetails']['videoId']

    while 'nextPageToken' in r.keys():
      r = self.__yt.playlistItems().list(part='contentDetails',playlistId=id, maxResults=50, pageToken=r['nextPageToken']).execute()
      for result in r.get('items', []):
        yield result['contentDetails']['videoId']

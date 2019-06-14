import requests

class BeetrackUploader:
  BEETRACK_URL = 'https://app.beetrack.com/api/external/v1/import'

  def __init__(self, api_key):
    self.headers = {
          'X-AUTH-TOKEN': api_key
        }

  def upload(self, file_path):
    files = {'file': open(file_path, 'rb')}
    res = requests.post(self.BEETRACK_URL, headers=self.headers, files=files)
    return res


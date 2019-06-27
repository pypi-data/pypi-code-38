import requests
import base64

def uploadImage(filename):
    '''
            Uploads image to Texternet and returns URL of file
    '''
    f = open(filename, 'rb')
    image_read = f.read()
    image_64_encode = base64.encodestring(image_read)
    API_ENDPOINT = "https://texternet.tk/api/image"
    data = {'image': image_64_encode}
    r = requests.post(url = API_ENDPOINT, data = data) 

    return r.text

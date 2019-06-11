from requests_futures.sessions import FuturesSession


class publisherSocketIo():
    """Publish message using socketIo.
    
    Parameters
    ----------
    url: str
        URL to post messages to
    api_key: str
        API key
    endpoint: str
        Socket IO endpoint. Default = 'logEvent'
    """
    def __init__(self, url, api_key, endpoint='logEvent'):
        # Initialise socketIo
        sio = socketio.Client()
        sio.connect(host,
            headers={
                'Authorization': api_key
            })
        self.sio = sio
        
        # Define socketIo endpoint
        self.endpoint = endpoint
    
    
    def emit(message, callback):
        """Publish message
        
        Parameters
        ----------
        message: dict
            Message to push to Stakion.
        callback: func
            The callback function is called when the message is acknowledges.
        """
        self.sio.emit(
            endpoint=self.endpoint,
            message=message,
            callback=self._remove_pending)
    
class publisherPost():
    """Publish message using POST.
    
    Parameters
    ----------
    url: str
        URL to post messages to
    api_key: str
        API key
    """
    def __init__(self, url, api_key):
        self.url = url
        self.session = FuturesSession()
        self.session.headers['authorization'] = api_key

        
    def emit(self, message, callback):
        """Publish message
        
        Parameters
        ----------
        message: dict
            Message to push to Stakion.
        callback: func
            The callback function is called when the message is acknowledges.
        """
        def response_hook(resp, *args, **kwargs):
            if resp.status_code == 200:
                callback(message['__uuid'])
            else:
                print(resp.content)
        
        future = self.session.post(self.url, json={'log': message}, hooks={
            'response': response_hook
        })
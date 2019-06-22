configs = {'F/mph': 'us12', 'C/ms': 'si12', 'C/kmh': 'ca12', 'C/mph': 'uk212'}


def check_values(forecast_self, latitude, longitude, config_mode, custom_url):
    """ A function to check if values are valid or are none

    Parameters:
    forecast_self: the self variable from forecast
    latitude (float): The latitude of the point you wish to forcast from
    longitude (float): The longitude of the point you wish to forcast from
    config_mode (str): The units of the returned dataset, should be in:  ('F/mph', C/ms', 'C/kmh', 'C/mph')
    custom_url (str): A different darknet URL (instead of 'https://darksky.net/forecast/[latitude],[longitude]/[config_mode]/en')

    Returns:
    tuple: Fixed and updated values:
        (latitude, longitude, config_mode, url)
    """
    self = forecast_self
    if latitude is None:
        if hasattr(self, 'latitude'):
            latitude = self.latitude
        else:
            raise ValueError('Latitude needs to be a specified value')
    if longitude is None:
        if hasattr(self, 'longitude'):
            longitude = self.longitude
        else:
            raise ValueError('Longitude needs to be a specified value')
    if config_mode is None:
        if hasattr(self, 'config_mode'):
            config_mode = self.config_mode
        else:
            raise ValueError('Config needs to be a specified value')
    if not config_mode in configs.keys():
        raise ValueError(f'config_mode must be one of these values: {list(configs.keys())}')
    
    if custom_url is None:
        url = f'https://darksky.net/forecast/{latitude},{longitude}/{configs[config_mode]}/en'
    else:
        if validate_url(custom_url) is None:
            raise ValueError(f'{custom_url} is not a valid URL')
        else:
            url = custom_url
    return (latitude, longitude, config_mode, url)

@staticmethod
def validate_url(url):
    """ A function that returns None if url is not valid (requires http(s))
    
    Parameters:
    url (str): The url to validate

    Returns:
    None (url not valid)
    """
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url)

from bs4 import BeautifulSoup
import re
import time
from .check_values import *
try:
    import urllib2.urlopen as urlopen
except:
    from urllib.request import urlopen


configs = {'F/mph': 'us12', 'C/ms': 'si12', 'C/kmh': 'ca12', 'C/mph': 'uk212'}

    
class forecast:
    ''' A class to scrape forcasting data from darksky.net '''
    def __init__(self, latitude=None, longitude=None, date=None, config_mode='C/ms', custom_url=None):
        ''' Initialize scraping environment '''

        self.latitude = latitude
        self.longitude = longitude
        self.config_mode = config_mode

        if custom_url is None:
            self.url = f'https://darksky.net/details/{latitude},{longitude}/{configs[config_mode]}/en'
        else:
            if validate_url(custom_url) is None:
                if custom_url[0:3] != 'http':
                    raise ValueError(f'{custom_url} is not a valid URL - Missing http(s)')
                else:
                    raise ValueError(f'{custom_url} is not a valid URL')
                
            else:
                self.url = custom_url

        if date is None:
            self.date = datetime.datetime.now().strftime("%Y-%m-%d")
        else:
            if validate_date(date):
                self.date = date
            else:
                raise ValueError('Date should be written in format: YYYY/MM/DD')


    def get_raw_data(self, latitude=None, longitude=None, date=None, config_mode=None, custom_url=None):
        """ A function that returns the raw variables from darksky.net in dict form.

        Parameters:
        latitude (float): The latitude of the point you wish to forcast from
        longitude (float): The longitude of the point you wish to forcast from
        config_mode (str): The units of the returned dataset, should be in:  ('F/mph', C/ms', 'C/kmh', 'C/mph')
        custom_url (str): A different darknet URL (instead of 'https://darksky.net/details/[latitude],[longitude]/[date]/[config_mode]/en')
        
        Returns:
        dict: vals 
            e.g. https://pastebin.com/basQJifK
        """
        latitude, longitude, date, config_mode, url = check_values(self, latitude, longitude, date, config_mode, custom_url)
        page = urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')
        for script in soup.find_all("script", {"src":False}):
            if script:
                values = re.findall(r'var.*?=\s*(.*?);', script.text, re.DOTALL | re.MULTILINE)
                for value in values:
                    vals = ({key: eval(val) for key, val in [x.split('=') for x in ('hours=' + value.replace(' ', '').replace(',\n', '\n').replace('false', 'False').replace('true', 'True').replace('null', '"Null"').replace('undefined', '"undefined"')).split('\n')]})

        return vals

    def get_overtime_raw_data(self, latitude=None, longitude=None, date=None, config_mode=None, custom_url=None):
        """ A function that returns get_raw_data['hours'] but specifies epoch time and gives local time

        Parameters:
        latitude (float): The latitude of the point you wish to forcast from
        longitude (float): The longitude of the point you wish to forcast from
        config_mode (str): The units of the returned dataset, should be in:  ('F/mph', C/ms', 'C/kmh', 'C/mph')
        custom_url (str): A different darknet URL (instead of 'https://darksky.net/details/[latitude],[longitude]/[date]/[config_mode]/en')
        
        Returns:
        array: vals 
            e.g. https://pastebin.com/9crC8ge6
        """
        
        vals = self.get_raw_data(latitude, longitude, date, config_mode, custom_url)['hours']
        for hour_period in vals:
            hour_period['epoch time'] = hour_period['time']
            hour_period['time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(hour_period['epoch time']))
        return vals

    def get_curr_temps(self, latitude=None, longitude=None, config_mode=None, custom_url=None):
        """ A function that returns the values of this bar: http://i.imgur.com/Nj2qbjq.png

        Parameters:
        latitude (float): The latitude of the point you wish to forcast from
        longitude (float): The longitude of the point you wish to forcast from
        config_mode (str): The units of the returned dataset, should be in:  ('F/mph', C/ms', 'C/kmh', 'C/mph')
        custom_url (str): A different darknet URL (instead of 'https://darksky.net/details/[latitude],[longitude]/[date]/[config_mode]/en')

        Returns:
        dict: {'feels like': [value],
               'low': [value],
               'high': [value]
              }
        """
        date = None
        latitude, longitude, date, config_mode, url = check_values(self, latitude, longitude, date, config_mode, custom_url)
        url = f'https://darksky.net/forecast/{latitude},{longitude}/{configs[config_mode]}/en'
        page = urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')
        temp_dict = {}
        for temp in soup.find_all('span', attrs={'class': 'high-low-label'}):
            if temp.text == 'Low: ':
                temp_dict['low'] = float(re.findall(r'\d+', temp.parent.text)[0])
            elif temp.text == 'High: ':
                temp_dict['high'] = float(re.findall(r'\d+', temp.parent.text)[0])
            elif temp.text == 'Feels Like: ':
                temp_dict['feels like'] = float(re.findall(r'\d+', temp.parent.text)[0])
        return temp_dict

    def get_curr_stats(self, latitude=None, longitude=None, date=None, config_mode=None, custom_url=None):
        """ A function that returns the values of this bar: http://i.imgur.com/frvlQ8g.png

        Parameters:
        latitude (float): The latitude of the point you wish to forcast from
        longitude (float): The longitude of the point you wish to forcast from
        config_mode (str): The units of the returned dataset, should be in:  ('F/mph', C/ms', 'C/kmh', 'C/mph')
        custom_url (str): A different darknet URL (instead of 'https://darksky.net/details/[latitude],[longitude]/[date]/[config_mode]/en')

        Returns:
        dict: {[attr]: {'value': [value]
                        'unit': [unit]}
              }
        """
        latitude, longitude, date, config_mode, url = check_values(self, latitude, longitude, date, config_mode, custom_url)
        page = urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')
        details = {}
        for div in soup.find('div', attrs={'id': 'currentDetails'}).find_all('div'):    
            if div['class'][0] != 'current_details_break':
                details[div['class'][0]] = {}
                if (div.find('span', attrs={'class': 'num swip'})) != None:
                    details[div['class'][0]]['value'] = float(div.find('span', attrs={'class': 'num swip'}).text)
                else:
                    if (div.find('span', attrs={'class': 'val swap'})) != None:
                        details[div['class'][0]]['value'] = float((div.find('span', attrs={'class': 'val swap'})).find('span', attrs={'class': 'num'}).text)
    
                if (div.find('span', attrs={'class': 'unit swap'})) != None:
                    details[div['class'][0]]['unit'] = div.find('span', attrs={'class': 'unit swap'}).text
                else:
                    unit = (div.find('span', attrs={'class': 'val swap'})).find('span', attrs={'class': 'unit'})
                    if unit != None:
                        details[div['class'][0]]['unit'] = unit.text
                    else:
                        details[div['class'][0]]['unit'] = None
        return details
                        
    def get_forecast(self, latitude=None, longitude=None, date=None, config_mode=None, custom_url=None):
        """ A function that joins get_curr_temps, get_curr_stats and get_overtime_raw_data into one return

        Parameters:
        latitude (float): The latitude of the point you wish to forcast from
        longitude (float): The longitude of the point you wish to forcast from
        config_mode (str): The units of the returned dataset, should be in:  ('F/mph', C/ms', 'C/kmh', 'C/mph')
        custom_url (str): A different darknet URL (instead of 'https://darksky.net/details/[latitude],[longitude]/[date]/[config_mode]/en')

        Returns:
        dict: {'temperatures': get_curr_temps(Parameters) 
               'weather data': get_curr_stats(Parameters)
               'overtime raw data': get_overtime_raw_data(Parameters)}
        """
        latitude, longitude, date, config_mode, url = check_values(self, latitude, longitude, date, config_mode, custom_url)
        return {'temperatures': self.get_curr_temps(latitude, longitude, date, config_mode, url), 
                'weather data': self.get_curr_stats(latitude, longitude, date, config_mode, url), 
                'overtime raw data': self.get_overtime_raw_data(latitude, longitude, date, config_mode, url)}






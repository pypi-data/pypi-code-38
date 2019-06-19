import urllib.request as urllib
import datetime
import numpy as np
from scipy.io import wavfile

''' 
#Example Location:
    'Cachiyuyo, Chile': {
        'loc_network': 'IU',
        'loc_station': 'LCO',
        'loc_code': '10'
    }
'''

class SeismicStation:
    def __init__(self, network, station, location):
        self.network = network
        self.station = station
        self.location = location

def getRawData(seismic_station, start_datetime, duration=3600, channel='BHZ', get_plot=False):
    '''
    Params:
    -seismic_station: (SEISMIC_STATION OBJECT) seismic station object
    -start_datetime: (DATETIME OBJECT) datetime object from which the sample should be taken
    -duration: (INT, OPTIONAL) duration of the sample in seconds
    -channel: (STRING, OPTIONAL) channel from which the data is taken (controls # of points)

    Returns:
    -An tuple containing an the header for the response and an array containing the magnitude sound data at each time interval
    '''

    def isNumber(num):
        try:
            float(num)
            return True
        except:
            return False

    assert seismic_station.network and seismic_station.station and seismic_station.location, "seismic_station must be a valid instance of the SeismicStation class."
    assert isinstance(start_datetime, datetime.datetime), "start_datetime must be a datetime created via the datetime module."
    assert isNumber(duration), "Please enter a valid duration."
    assert channel in ['BHZ', 'LHZ'], "Only BHZ and LHZ channels are supported."

    network = '?net=' + seismic_station.network
    station = "&sta=" + seismic_station.station
    location = "&loc=" + seismic_station.location
    channel = "&cha=" + channel

    date = "&starttime=" + str(start_datetime.date())
    time = "T" + str(start_datetime.time()).split('.')[0]

    iris_url_header = "http://service.iris.edu/irisws/timeseries/1/query"
    iris_body = network + station + location + channel
    iris_datetime = date + time + "&duration=" + str(int(duration))
    iris_footer = "&demean=true&scale=auto&output=ascii1"
    iris_url = iris_url_header + iris_body + iris_datetime + iris_footer

    print("Requesting data from IRIS...")
    try:
        ws = urllib.urlopen(iris_url)
    except:
        raise Exception('Error retrieving data from IRIS.')

    print("Loading Data...")
    try:
        df = ws.read().decode()
        dflines = df.split('\n')
    except:
        raise Exception('Data is malformed or corrupted and could not be parsed.')

    return dflines[0], [float(i) for i in dflines[1:] if isNumber(i)]

def generateAudioFile(sound_array, sampling_rate=44100, soundname='pyquake_audio', amp_level=1):
    '''
    Params:
    -sound_array: array of points representing a sound wave
    -sampling_rate: (OPTIONAL) number of samples per second to represent
    -soundname: (OPTIONAL) path to location and name of .wav file
    -amp_level: (OPTIONAL) modifier used to manipulate audio amplitude level

    Returns:
    -A scaled audio array containing the magnitude sound data at each time interval
    '''
    assert amp_level <= 1 and amp_level > 0, 'Amplitude Level must be greater than 0 and less than or equal to 1.'

    def isNumber(num):
        try:
            float(num)
            return True
        except:
            return False

    max_point = max(sound_array)
    if (len(sound_array)) <= 2 or not isNumber(max_point):
        print("WARNING: The function getRawData returns a tuple containing the request header and the audio array. Make sure to pass in the correct value.")
        return
    scaled_amp = max(sound_array) * amp_level
    sound = np.asarray(sound_array)
    scaled_audio = (2**31) * np.arctan(sound / scaled_amp) / (0.5 * np.pi)
    s32 = np.int32(scaled_audio)

    if (".wav" not in soundname):
        soundname += ".wav"
    print("Creating audio file...")
    wavfile.write(soundname, int(sampling_rate), s32)

    return s32

station = SeismicStation('IU', 'LCO', '10')
s = getRawData(station, datetime.datetime(2019, 6, 1))[0]
generateAudioFile(s)
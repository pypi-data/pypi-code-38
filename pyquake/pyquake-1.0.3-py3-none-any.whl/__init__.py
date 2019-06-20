import urllib.request as urllib
import datetime, math, mpu
import numpy as np
from scipy.io import wavfile

class SeismicStation:
    def __init__(self, network, station, location="", name="", latitude=0.0, longitude=0.0):
        self.network = network
        self.station = station
        self.name = name
        self.location = location
        self.latitude = latitude
        self.longitude = longitude
    
    def __repr__(self):
        return self.name if self.name != '' else self.network

#alias for makeIrisRequest with no params
def getAllStations():
    return makeIrisStationRequest()

def getStations(network="", station=""):
    '''
    Params:
    -network: (STRING, OPTIONAL) Network code to search for. Defaults to empty, which will search all codes.
    -station: (STRING, OPTIONAL) Station code to search for. Defaults to empty, which will search all codes.
    '''
    params = f"{f'&net={network}' if network else ''}{f'&sta={station}' if station else ''}"
    return makeIrisStationRequest(params)

def makeIrisStationRequest(params=''):
    '''
    Params:
    -params: (STRING) string representation of query parameters

    Returns:
    -An array of SeismicStation objects
    '''
    try:
        ws = urllib.urlopen("http://service.iris.edu/fdsnws/station/1/query?format=text" + params)
    except:
        raise Exception("ERROR: Could not retrieve data from IRIS.")

    try:
        ws_arr = ws.read().decode().split("\n")
    except:
        raise Exception("ERROR: Data could not be parsed.")

    if len(ws_arr) == 1: #only header was returned
        return []

    station_arr = []
    for station in ws_arr[1:]:
        if station:
            split_station = station.split("|")
            new_station = SeismicStation(split_station[0], split_station[1], name=split_station[5], latitude=float(split_station[2]), longitude=float(split_station[3]))
            station_arr.append(new_station)
    return station_arr

def getNearestStation(latitude, longitude, stations):
    '''
    Params:
    -latitude: (FLOAT) latitude of coordinate
    -longitude: (FLOAT) longitude of coordinate
    -stations: ([SeismicStation]) array of seismic stations to search through

    Returns:
    -A SeismicStation object representing the closest seismic station to the given coordinate
    '''
    if len(stations) == 0 or not stations[0].network or not stations[0].station:
        raise Exception("stations must be a valid SeismicStation array")
    elif len(stations) == 1:
        return stations[0]

    test_coordinate = (latitude, longitude)

    nearest_station = stations[0]
    nearest_distance = math.inf
    for station in stations[1:]:
        station_coordinate = (station.latitude, station.longitude)
        try:
            distance = mpu.haversine_distance(test_coordinate, station_coordinate)
        except:
            continue
        if distance < nearest_distance:
            nearest_station = station
            nearest_distance = distance
    return nearest_station

#Takes in station and time info and returns an array representation of audio.
def getRawData(seismic_station, start_datetime, duration=3600, channel='BHZ'):
    '''
    Params:
    -seismic_station: (SEISMIC_STATION OBJECT) seismic station object
    -start_datetime: (DATETIME OBJECT) datetime object from which the sample should be taken
    -duration: (INT, OPTIONAL) duration of the sample in seconds
    -channel: (STRING, OPTIONAL) channel from which the data is taken (controls # of points)

    Returns:
    -A tuple containing the header for the IRIS response and an array containing the magnitude sound data.
    '''

    supported_locations = ["--", "00", "10", "20"]
    def isNumber(num):
        try:
            float(num)
            return True
        except:
            return False

    assert seismic_station.network and seismic_station.station, "seismic_station must be a valid instance of the SeismicStation class."
    assert isinstance(start_datetime, datetime.datetime), "start_datetime must be a datetime created via the Python datetime module."
    assert start_datetime < datetime.datetime.now(), "start_datetime cannot be in the future."
    assert isNumber(duration), "Please enter a valid duration."
    assert float(duration) < 2_592_000, "Time series requested must not exceed 30 days."
    assert channel in ["BHZ", "LHZ"], "Only BHZ and LHZ channels are supported."

    network = f"?net={seismic_station.network}"
    station = f"&sta={seismic_station.station}"
    locations = supported_locations if seismic_station.location not in supported_locations else [seismic_station.location]
    channel = f"&cha={channel}"

    date = "&starttime=" + str(start_datetime.date())
    time = "T" + str(start_datetime.time()).split('.')[0]

    iris_url_header = "http://service.iris.edu/irisws/timeseries/1/query"
    iris_datetime = date + time + "&duration=" + str(int(duration))
    iris_footer = "&demean=true&scale=auto&output=ascii1"

    print(f"Requesting data from IRIS...")
    ws = None
    for location in locations:
        if len(locations) > 1:
            print(f"Trying location {location} for station {seismic_station.station}...")
        iris_body = network + station + f"&loc={location}" + channel
        iris_url = iris_url_header + iris_body + iris_datetime + iris_footer
  
        try:
            ws = urllib.urlopen(iris_url)
            break
        except:
            continue
    if ws is None:
        raise Exception("ERROR: Could not retrieve data from IRIS.")

    print("Loading Data...")
    try:
        df = ws.read().decode()
        dflines = df.split('\n')
    except:
        raise Exception("ERROR: Data could not be parsed.")

    return dflines[0], [float(i) for i in dflines[1:] if isNumber(i)]

#Saves an audio file generated from an array representation to the working directory
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

    max_point = max(sound_array)
    if (len(sound_array)) <= 2:
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
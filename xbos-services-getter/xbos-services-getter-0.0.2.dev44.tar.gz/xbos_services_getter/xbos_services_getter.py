import grpc
from xbos_services_getter.lib import building_zone_names_pb2
from xbos_services_getter.lib import building_zone_names_pb2_grpc
from xbos_services_getter.lib import hvac_consumption_pb2
from xbos_services_getter.lib import hvac_consumption_pb2_grpc
from xbos_services_getter.lib import indoor_data_historical_pb2
from xbos_services_getter.lib import indoor_data_historical_pb2_grpc
from xbos_services_getter.lib import indoor_temperature_prediction_pb2
from xbos_services_getter.lib import indoor_temperature_prediction_pb2_grpc
from xbos_services_getter.lib import meter_data_historical_pb2
from xbos_services_getter.lib import meter_data_historical_pb2_grpc
from xbos_services_getter.lib import occupancy_pb2
from xbos_services_getter.lib import occupancy_pb2_grpc
from xbos_services_getter.lib import optimizer_pb2
from xbos_services_getter.lib import optimizer_pb2_grpc
from xbos_services_getter.lib import outdoor_temperature_historical_pb2
from xbos_services_getter.lib import outdoor_temperature_historical_pb2_grpc
from xbos_services_getter.lib import outdoor_temperature_prediction_pb2
from xbos_services_getter.lib import outdoor_temperature_prediction_pb2_grpc
from xbos_services_getter.lib import price_pb2
from xbos_services_getter.lib import price_pb2_grpc
from xbos_services_getter.lib import temperature_bands_pb2
from xbos_services_getter.lib import temperature_bands_pb2_grpc
from xbos_services_getter.lib import baseline_optimizer_pb2
from xbos_services_getter.lib import baseline_optimizer_pb2_grpc

import datetime
import pytz
import pandas as pd

import os

'''
Utility constants
'''
NO_ACTION = 0
HEATING_ACTION = 1
COOLING_ACTION = 2
FAN = 3
TWO_STAGE_HEATING_ACTION = 4
TWO_STAGE_COOLING_ACTION = 5

def get_window_in_sec(s):
    """Returns number of seconds in a given duration or zero if it fails.
    Supported durations are seconds (s), minutes (m), hours (h), and days(d)."""
    seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    try:
        return int(float(s[:-1])) * seconds_per_unit[s[-1]]
    except:
        return 0


# Building and Zone names
def get_building_zone_names_stub(BUILDING_ZONE_NAMES_HOST_ADDRESS=None,secure=True):
    """Get the stub to interact with the building_zone_address service.

    :param BUILDING_ZONE_NAMES_HOST_ADDRESS: Optional argument to supply host address for given service. Otherwise,
        set as environment variable.
    :return: grpc Stub object.

    """

    if BUILDING_ZONE_NAMES_HOST_ADDRESS is None:
        BUILDING_ZONE_NAMES_HOST_ADDRESS = os.environ["BUILDING_ZONE_NAMES_HOST_ADDRESS"]

    if not secure:
        channel = grpc.insecure_channel(BUILDING_ZONE_NAMES_HOST_ADDRESS)
    else:
        credentials = grpc.ssl_channel_credentials()
        channel = grpc.secure_channel(BUILDING_ZONE_NAMES_HOST_ADDRESS, credentials)
    return building_zone_names_pb2_grpc.BuildingZoneNamesStub(channel)



def get_buildings(building_zone_names_stub):
    """Gets all the building names supported by the services.

    :param building_zone_names_stub: grpc stub for building_zone_names service.
    :return: list (string) building names.

    """

    building_names = building_zone_names_stub.GetBuildings(building_zone_names_pb2.BuildingRequest())
    return [bldg.name for bldg in building_names.names]


def get_zones(building_zone_names_stub, building):
    """Gets all zone names for the given building which are supported by the services.

    :param building_zone_names_stub: grpc stub for building_zone_names service.
    :param building: (string) building name. Needs to be in the list returned by get_buildings.
    :return: list (string) zone names.

    """
    zones = building_zone_names_stub.GetZones(building_zone_names_pb2.ZoneRequest(building=building))
    return [zone.name for zone in zones.names]


def get_all_buildings_zones(building_zone_names_stub):
    """Gets all building and corresponding zones in a dictionary.

    :param building_zone_names_stub: grpc stub for building_zone_names service.
    :return: dictionary <building name, list<zone names>> (strings)

    """
    buildings = get_buildings(building_zone_names_stub)
    zones = {}

    for bldg in buildings:
        zones[bldg] = get_zones(building_zone_names_stub, bldg)

    return zones


# Temperature band functions
def get_temperature_band_stub(TEMPERATURE_BANDS_HOST_ADDRESS=None,secure=True):
    """Get the stub to interact with the temperature_band service.

    :param TEMPERATURE_BANDS_HOST_ADDRESS: Optional argument to supply host address for given service. Otherwise,
        set as environment variable.
    :return: grpc Stub object.

    """

    if TEMPERATURE_BANDS_HOST_ADDRESS is None:
        TEMPERATURE_BANDS_HOST_ADDRESS = os.environ["TEMPERATURE_BANDS_HOST_ADDRESS"]
    if not secure:
        channel = grpc.insecure_channel(TEMPERATURE_BANDS_HOST_ADDRESS)
    else:
        credentials = grpc.ssl_channel_credentials()
        channel = grpc.secure_channel(TEMPERATURE_BANDS_HOST_ADDRESS, credentials)
    return temperature_bands_pb2_grpc.SchedulesStub(channel)


def get_comfortband(temperature_band_stub, building, zone, start, end, window):
    """Gets comfortband as pd.df.

    :param temperature_band_stub: grpc stub for temperature_band microservice
    :param building: (str) building name
    :param zone: (str) zone name
    :param start: (datetime timezone aware) start of comfortband
    :param end: (datetime timezone aware) end of comfortband
    :param window: (str) the interval in which to split the comfortband.
    :return: pd.df columns=["t_low", "t_high"], valus=float, index=time

    """
    start = start.replace(microsecond=0)
    end = end.replace(microsecond=0)

    start_unix = start.timestamp() * 1e9
    end_unix = end.timestamp() * 1e9
    window_seconds = get_window_in_sec(window)

    # call service
    comfortband_response = temperature_band_stub.GetComfortband(
        temperature_bands_pb2.ScheduleRequest(building=building, zone=zone, start=int(start_unix), end=int(end_unix), window=window,
                              unit="F"))

    # process data
    comfortband_list = []
    for msg in comfortband_response:
        item = {
            "datetime" : datetime.datetime.utcfromtimestamp(msg.time / 1e9).replace(tzinfo=pytz.utc).astimezone(tz=start.tzinfo),
            "t_high" : msg.temperature_high,
            "t_low" : msg.temperature_low,
            "unit" : msg.unit
        }
        comfortband_list.append(item)
    df = pd.DataFrame(comfortband_list)
    df.set_index("datetime",inplace=True)
    return df


def get_do_not_exceed(temperature_band_stub, building, zone, start, end, window):
    """Gets do_not_exceed as pd.df.

    :param temperature_band_stub: grpc stub for temperature_band microservice
    :param building: (str) building name
    :param zone: (str) zone name
    :param start: (datetime timezone aware) start of do_not_exceed
    :param end: (datetime timezone aware) end of do_not_exceed
    :param window: (str) the interval in which to split the do_not_exceed.
    :return: pd.df columns=["t_low", "t_high"], valus=float, index=time

    """
    start = start.replace(microsecond=0)
    end = end.replace(microsecond=0)

    start_unix = start.timestamp() * 1e9
    end_unix = end.timestamp() * 1e9
    window_seconds = get_window_in_sec(window)

    # call service
    do_not_exceed_response = temperature_band_stub.GetDoNotExceed(
        temperature_bands_pb2.ScheduleRequest(building=building, zone=zone, start=int(start_unix), end=int(end_unix), window=window,
                              unit="F"))

    # process data
    do_not_exceed_list = []
    for msg in do_not_exceed_response:
        item = {
            "datetime" : datetime.datetime.utcfromtimestamp(msg.time / 1e9).replace(tzinfo=pytz.utc).astimezone(tz=start.tzinfo),
            "t_high" : msg.temperature_high,
            "t_low" : msg.temperature_low,
            "unit" : msg.unit
        }
        do_not_exceed_list.append(item)
    df = pd.DataFrame(do_not_exceed_list)
    df.set_index("datetime",inplace=True)
    return df


# occupancy functions
def get_occupancy_stub(OCCUPANCY_HOST_ADDRESS=None,secure=True):
    """Get the stub to interact with the occupancy service.

    :param OCCUPANCY_HOST_ADDRESS: Optional argument to supply host address for given service. Otherwise,
        set as environment variable.
    :return: grpc Stub object.

    """
    if OCCUPANCY_HOST_ADDRESS is None:
        OCCUPANCY_HOST_ADDRESS = os.environ["OCCUPANCY_HOST_ADDRESS"]

    if not secure:
        channel = grpc.insecure_channel(OCCUPANCY_HOST_ADDRESS)
    else:
        credentials = grpc.ssl_channel_credentials()
        channel = grpc.secure_channel(OCCUPANCY_HOST_ADDRESS, credentials)
    return occupancy_pb2_grpc.OccupancyStub(channel)


def get_occupancy(occupancy_stub, building, zone, start, end, window):
    """Gets occupancy as pd.series.

    :param occupancy_stub: grpc stub for occupancy microservice
    :param building: (str) building name
    :param zone: (str) zone name
    :param start: (datetime timezone aware)
    :param end: (datetime timezone aware)
    :param window: (str) the interval in which to split the data.
    :return: pd.series valus=float, index=time

    """
    start = start.replace(microsecond=0)
    end = end.replace(microsecond=0)

    start_unix = start.timestamp() * 1e9
    end_unix = end.timestamp() * 1e9
    window_seconds = get_window_in_sec(window)

    # call service
    occupancy_response = occupancy_stub.GetOccupancy(
        occupancy_pb2.Request(building=building, zone=zone, start=int(start_unix), end=int(end_unix), window=window))

    # process data
    occupancy_list = []
    for msg in occupancy_response:
        item = {
            "datetime" : datetime.datetime.utcfromtimestamp(msg.time / 1e9).replace(tzinfo=pytz.utc).astimezone(tz=start.tzinfo),
            "occupancy" : msg.occupancy
        }
        occupancy_list.append(item)
    df = pd.DataFrame(occupancy_list)
    df.set_index("datetime",inplace=True)
    return df


# price functions
def get_price_stub(PRICE_HOST_ADDRESS=None,secure=True):
    """Get the stub to interact with the price service.

    :param PRICEPRICE_HOST_ADDRESS: Optional argument to supply host address for given service. Otherwise,
        set as environment variable.
    :return: grpc Stub object.

    """
    if PRICE_HOST_ADDRESS is None:
        PRICE_HOST_ADDRESS = os.environ["PRICE_HOST_ADDRESS"]

    if not secure:
        channel = grpc.insecure_channel(PRICE_HOST_ADDRESS)
    else:
        credentials = grpc.ssl_channel_credentials()
        channel = grpc.secure_channel(PRICE_HOST_ADDRESS, credentials)
    return price_pb2_grpc.PriceStub(channel)

def get_all_tariffs(price_stub):
    """Gets all available tariffs and utilities as a list of dictionaries.

    :param price_stub: grpc stub for price microservice
    :return: list of (dictionary) keys=["tariff", "utility"]

    """
    all_tariffs_utilities = price_stub.GetAllTariffsAndUtilities(price_pb2.Empty()).tariffs_utilities
    all_tariffs_utilities_list = []
    for tariff_and_utility in all_tariffs_utilities:
        all_tariffs_utilities_list.append({"tariff": tariff_and_utility.tariff, "utility": tariff_and_utility.utility})
    return all_tariffs_utilities_list

def get_tariff_and_utility(price_stub, building):
    """Gets the tariff and utility for the given building as a dictionary.

    :param price_stub: grpc stub for price microservice
    :param building: (str) building name
    :return: (dictionary) keys=["tariff", "utility"]
    """
    tariff_and_utility = price_stub.GetTariffAndUtility(price_pb2.BuildingRequest(building=building))
    return {"tariff": tariff_and_utility.tariff, "utility": tariff_and_utility.utility}


def get_price_utility_tariff(price_stub,utility,tariff,price_type, start, end, window):
    """Gets the price as a pandas dataframe.

    :param price_stub: grpc stub for price microservice
    :param building: (str) building name
    :param price_type: (str) "ENERGY" or "DEMAND"
    :param start: (datetime timezone aware)
    :param end: (datetime timezone aware)
    :param window: (str) the interval in which to split the data.
    :return: pd.DataFrame columns=["price" (float), "unit" string] index=start to end with window intervals.
    """
    if price_type not in ["ENERGY", "DEMAND"]:
        raise AttributeError("Given price type is invalid. Use ENERGY or DEMAND.")

    start = start.replace(microsecond=0)
    end = end.replace(microsecond=0)

    start_unix = int(start.timestamp() * 1e9)
    end_unix = int(end.timestamp() * 1e9)
    window_seconds = get_window_in_sec(window)

    # call service
    price_response = price_stub.GetPrice(price_pb2.PriceRequest(utility=utility,
                                                       tariff=tariff,
                                                       price_type=price_type,
                                                       start=start_unix,
                                                       end=end_unix,
                                                       window=window))
    # process data
    utility_tariff_list = []
    for msg in price_response:
        item = {
            "datetime" : datetime.datetime.utcfromtimestamp(msg.time / 1e9).replace(tzinfo=pytz.utc).astimezone(tz=start.tzinfo),
            "price" : msg.price,
            "unit" : msg.unit,
            "window" : msg.window
        }
        utility_tariff_list.append(item)
    df = pd.DataFrame(utility_tariff_list)
    df.set_index("datetime",inplace=True)
    return df

def get_price(price_stub, building, price_type, start, end, window):
    """Gets the price as a pandas dataframe.

    :param price_stub: grpc stub for price microservice
    :param building: (str) building name
    :param price_type: (str) "ENERGY" or "DEMAND"
    :param start: (datetime timezone aware)
    :param end: (datetime timezone aware)
    :param window: (str) the interval in which to split the data.
    :return: pd.DataFrame columns=["price", "unit"], types=[float, string] index=start to end with window intervals.
    """

    # call service
    tariff_and_utility = get_tariff_and_utility(price_stub, building)
    return get_price_utility_tariff(price_stub,tariff_and_utility["utility"],tariff_and_utility["tariff"],price_type, start, end, window)


def get_demand_response_forecast_utility(price_stub, utility,timezone=pytz.timezone('US/Pacific')):
    if utility.upper() not in ["PGE", "SCE"]:
        raise AttributeError("Given utility type is invalid. Use PGE or SCE.")
    # call service
    demand_response = price_stub.GetDemandResponseForecast(price_pb2.DemandResponseRequest(utility=utility)).statuses
    # process data
    utility_tariff_list = []
    for msg in demand_response:
        item = {
            "datetime" : datetime.datetime.utcfromtimestamp(msg.time / 1e9).replace(tzinfo=pytz.utc).astimezone(tz=timezone),
            "status" : msg.status
        }
        utility_tariff_list.append(item)
    df = pd.DataFrame(utility_tariff_list)
    if len(utility_tariff_list)!= 0:
        df.set_index("datetime",inplace=True)
    return df


def get_demand_response_confirmed_utility(price_stub, utility,timezone=pytz.timezone('US/Pacific')):
    if utility.upper() not in ["PGE", "SCE"]:
        raise AttributeError("Given utility type is invalid. Use PGE or SCE.")
    # call service
    demand_response = price_stub.GetDemandResponseConfirmed(price_pb2.DemandResponseRequest(utility=utility)).statuses
    # process data
    utility_tariff_list = []
    for msg in demand_response:
        item = {
            "datetime" : datetime.datetime.utcfromtimestamp(msg.time / 1e9).replace(tzinfo=pytz.utc).astimezone(tz=timezone),
            "status" : msg.status
        }
        utility_tariff_list.append(item)

    df = pd.DataFrame(utility_tariff_list)
    if len(utility_tariff_list)!= 0:
        df.set_index("datetime",inplace=True)
    return df

def get_demand_response_forecast(price_stub, building,timezone=pytz.timezone('US/Pacific')):
    tariff_and_utility = get_tariff_and_utility(price_stub, building)
    return get_demand_response_forecast_utility(price_stub,tariff_and_utility["utility"])

def get_demand_response_confirmed(price_stub, building,timezone=pytz.timezone('US/Pacific')):
    tariff_and_utility = get_tariff_and_utility(price_stub, building)
    return get_demand_response_confirmed_utility(price_stub,tariff_and_utility["utility"])

# indoor historic functions
def get_indoor_historic_stub(INDOOR_DATA_HISTORICAL_HOST_ADDRESS=None,secure=True):
    """Get the stub to interact with the indoor_data_historical service.

    :param INDOOR_DATA_HISTORICAL_HOST_ADDRESS: Optional argument to supply host address for given service. Otherwise,
        set as environment variable.
    :return: grpc Stub object.

    """

    if INDOOR_DATA_HISTORICAL_HOST_ADDRESS is None:
        INDOOR_DATA_HISTORICAL_HOST_ADDRESS = os.environ["INDOOR_DATA_HISTORICAL_HOST_ADDRESS"]

    if not secure:
        channel = grpc.insecure_channel(INDOOR_DATA_HISTORICAL_HOST_ADDRESS)
    else:
        credentials = grpc.ssl_channel_credentials()
        channel = grpc.secure_channel(INDOOR_DATA_HISTORICAL_HOST_ADDRESS, credentials)
    return indoor_data_historical_pb2_grpc.IndoorDataHistoricalStub(channel)


def get_indoor_temperature_historic(indoor_historic_stub, building, zone, start, end, window, agg="MEAN"):
    """Gets historic indoor temperature as pd.series.

    :param indoor_historic_stub: grpc stub for historic indoor temperature microservice
    :param building: (str) building name
    :param zone: (str) zone name
    :param start: (datetime timezone aware)
    :param end: (datetime timezone aware)
    :param window: (str) the interval in which to split the data.
    :return: pd.df columns=["temperature", "unit"] values=[float, string], index=time

    """
    start = start.replace(microsecond=0)
    end = end.replace(microsecond=0)

    start_unix = int(start.timestamp() * 1e9)
    end_unix = int(end.timestamp() * 1e9)
    window_seconds = get_window_in_sec(window)

    # call service
    historic_temperature_response = indoor_historic_stub.GetRawTemperatures(
        indoor_data_historical_pb2.Request(building=building, zone=zone, start=start_unix, end=end_unix,
                                              window=window,aggregation=agg))

    # process data
    temperature_list = []
    for msg in historic_temperature_response:
        item = {
            "datetime" : datetime.datetime.utcfromtimestamp(msg.time / 1e9).replace(tzinfo=pytz.utc).astimezone(tz=start.tzinfo),
            "temperature" : msg.temperature,
            "unit" : msg.unit
        }
        temperature_list.append(item)

    df = pd.DataFrame(temperature_list)
    df.set_index("datetime",inplace=True)
    return df

def get_indoor_actions_historic(indoor_historic_stub, building, zone, start, end, window, agg="MAX"):
    """Gets historic indoor temperature as pd.series.

    :param indoor_historic_stub: grpc stub for historic indoor temperature microservice
    :param building: (str) building name
    :param zone: (str) zone name
    :param start: (datetime timezone aware)
    :param end: (datetime timezone aware)
    :param window: (str) the interval in which to split the data.
    :return: pd.df columns["action"], types=["float"], index=time

    """
    start = start.replace(microsecond=0)
    end = end.replace(microsecond=0)

    start_unix = int(start.timestamp() * 1e9)
    end_unix = int(end.timestamp() * 1e9)
    window_seconds = get_window_in_sec(window)

    # call service
    historic_action_response = indoor_historic_stub.GetRawActions(
        indoor_data_historical_pb2.Request(building=building, zone=zone, start=start_unix, end=end_unix,
                                              window=window,aggregation=agg))

    # process data
    action_list = []
    for msg in historic_action_response:
        item = {
            "datetime" : datetime.datetime.utcfromtimestamp(msg.time / 1e9).replace(tzinfo=pytz.utc).astimezone(tz=start.tzinfo),
            "action" : msg.action
        }
        action_list.append(item)
    df = pd.DataFrame(action_list)
    df.set_index("datetime",inplace=True)
    return df

def get_indoor_modes_historic(indoor_historic_stub, building, zone, start, end, window, agg="MAX"):
    """Gets historic indoor temperature as pd.series.

    :param indoor_historic_stub: grpc stub for historic indoor temperature microservice
    :param building: (str) building name
    :param zone: (str) zone name
    :param start: (datetime timezone aware)
    :param end: (datetime timezone aware)
    :param window: (str) the interval in which to split the data.
    :return: pd.df columns["mode"], types=["float"], index=time

    """
    start = start.replace(microsecond=0)
    end = end.replace(microsecond=0)

    start_unix = int(start.timestamp() * 1e9)
    end_unix = int(end.timestamp() * 1e9)
    window_seconds = get_window_in_sec(window)

    # call service
    historic_mode_response = indoor_historic_stub.GetRawModes(
        indoor_data_historical_pb2.Request(building=building, zone=zone, start=start_unix, end=end_unix,
                                              window=window,aggregation=agg))

    # process data
    mode_list = []
    for msg in historic_mode_response:
        item = {
            "datetime" : datetime.datetime.utcfromtimestamp(msg.time / 1e9).replace(tzinfo=pytz.utc).astimezone(tz=start.tzinfo),
            "mode" : msg.mode
        }
        mode_list.append(item)
    df = pd.DataFrame(mode_list)
    df.set_index("datetime",inplace=True)
    return df


def get_indoor_setpoints_historic(indoor_historic_stub, building, zone, start, end, window,agg="MIN"):
    """Gets historic setpoints temperature as pd.df.

    :param indoor_historic_stub: grpc stub for historic indoor temperature microservice
    :param building: (str) building name
    :param zone: (str) zone name
    :param start: (datetime timezone aware)
    :param end: (datetime timezone aware)
    :param window: (str) the interval in which to split the data.
    :return: pd.df columns=["t_low", "t_high"] valus=float, index=time

    """
    start = start.replace(microsecond=0)
    end = end.replace(microsecond=0)

    start_unix = int(start.timestamp() * 1e9)
    end_unix = int(end.timestamp() * 1e9)
    window_seconds = get_window_in_sec(window)

    # call service
    historic_setpoints_response = indoor_historic_stub.GetRawTemperatureBands(
        indoor_data_historical_pb2.Request(building=building, zone=zone, start=start_unix, end=end_unix,
                                              window=window,aggregation=agg))

    # process data
    setpoints_list = []
    for msg in historic_setpoints_response:
        item = {
            "datetime" : datetime.datetime.utcfromtimestamp(msg.time / 1e9).replace(tzinfo=pytz.utc).astimezone(tz=start.tzinfo),
            "t_high" : msg.temperature_high,
            "t_low" : msg.temperature_low,
            "unit" : msg.unit
        }
        setpoints_list.append(item)
    df = pd.DataFrame(setpoints_list)
    df.set_index("datetime",inplace=True)
    return df

# indoor prediction functions
def get_indoor_temperature_prediction_stub(INDOOR_TEMPERATURE_PREDICTION_HOST_ADDRESS=None,secure=True):
    """Get the stub to interact with the indoor_temperature_prediction service.

    :param INDOOR_TEMPERATURE_PREDICTION_HOST_ADDRESS: Optional argument to supply host address for given service. Otherwise,
        set as environment variable.
    :return: grpc Stub object.

    """

    if INDOOR_TEMPERATURE_PREDICTION_HOST_ADDRESS is None:
        INDOOR_TEMPERATURE_PREDICTION_HOST_ADDRESS = os.environ["INDOOR_TEMPERATURE_PREDICTION_HOST_ADDRESS"]

    if not secure:
        channel = grpc.insecure_channel(INDOOR_TEMPERATURE_PREDICTION_HOST_ADDRESS)
    else:
        credentials = grpc.ssl_channel_credentials()
        channel = grpc.secure_channel(INDOOR_TEMPERATURE_PREDICTION_HOST_ADDRESS, credentials)
    return indoor_temperature_prediction_pb2_grpc.IndoorTemperaturePredictionStub(channel)


def get_indoor_temperature_prediction(indoor_temperature_prediction_stub, building, zone, current_time, action, t_in, t_out, t_prev,
                                      other_zone_temperatures):
    """Gets prediction of indoor temperature.

    :param indoor_temperature_prediction_stub: grpc stub for prediction of indoor temperature microservice
    :param building: (str) building name
    :param zone: (str) zone name
    :param current_time: (datetime timezone aware)
    :param action: (int) Action as given in utils file.
    :param t_in: (float) current temperature inside of zone.
    :param t_out: (float) currrent outdoor temperature.
    :param t_prev: (float) the temperature 5 min ago.
    :param other_zone_temperatures: {zone_i: indoor temperature of zone_i}
    :return: (float) temperature in 5 minutes after current_time in Fahrenheit.

    """
    current_time = current_time.replace(microsecond=0)

    current_time_unix = int(current_time.timestamp() * 1e9)

    # call service
    indoor_prediction_response = indoor_temperature_prediction_stub.GetSecondOrderPrediction(
        indoor_temperature_prediction_pb2.SecondOrderPredictionRequest(building=building, zone=zone, current_time=current_time_unix,
                                              action=action,
                                              indoor_temperature=t_in, previous_indoor_temperature=t_prev,
                                                                       outside_temperature=t_out,
                                              other_zone_temperatures=other_zone_temperatures,
                                              temperature_unit="F"))

    return indoor_prediction_response.temperature,datetime.datetime.utcfromtimestamp(indoor_prediction_response.time / 1e9).replace(tzinfo=pytz.utc).astimezone(tz=current_time.tzinfo),indoor_prediction_response.unit

def get_indoor_temperature_prediction_error(indoor_temperature_prediction_stub, building, zone, action, start=None, end=None,
                                            temperature_unit="F"):
    """Gets mean and var of the error of indoor temperature predictions.

    :param indoor_temperature_prediction_stub: grpc stub for prediction of indoor temperature microservice
    :param building: (str) building name
    :param zone: (str) zone name
    :param action: (int) Action as given in utils file. Specifies for which action to get the error. -1 gets the error
        on the whole dataset, regardless of action.
    :param start: (datetime timezone aware). If None, get the training error.
    :param end: (datetime timezone aware). If None, get the training error.
    :param temperature_unit: temperature unit
    :return: mean error (float), varirance of error (float), unit of the error (string).
    """
    if (start is None) or (end is None):
        end = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        start = end - datetime.timedelta(hours=24)

    start = start.replace(microsecond=0)
    end = end.replace(microsecond=0)

    start_unix = int(start.timestamp() * 1e9)
    end_unix = int(end.timestamp() * 1e9)

    # call service
    error_response = indoor_temperature_prediction_stub.GetSecondOrderError(
        indoor_temperature_prediction_pb2.ErrorRequest(building=building, zone=zone, action=action,
                                              start=start_unix,
                                              end=end_unix,
                                              unit=temperature_unit))

    return error_response.mean, error_response.var, error_response.unit

# HVAC Consumption functions
def get_hvac_consumption_stub(HVAC_CONSUMPTION_HOST_ADDRESS=None,secure=True):
    """Get the stub to interact with the hvac_consumption service.

    :param HVAC_CONSUMPTION_HOST_ADDRESS: Optional argument to supply host address for given service. Otherwise,
        set as environment variable.
    :return: grpc Stub object.

    """

    if HVAC_CONSUMPTION_HOST_ADDRESS is None:
        HVAC_CONSUMPTION_HOST_ADDRESS = os.environ["HVAC_CONSUMPTION_HOST_ADDRESS"]

    if not secure:
        channel = grpc.insecure_channel(HVAC_CONSUMPTION_HOST_ADDRESS)
    else:
        credentials = grpc.ssl_channel_credentials()
        channel = grpc.secure_channel(HVAC_CONSUMPTION_HOST_ADDRESS, credentials)
    return hvac_consumption_pb2_grpc.ConsumptionHVACStub(channel)


def get_hvac_consumption(hvac_consumption_stub, building, zone):
    hvac_consumption_response = hvac_consumption_stub.GetConsumption(
        hvac_consumption_pb2.Request(building=building, zone=zone))

    hvac_consumption_final = {NO_ACTION: 0,
                              HEATING_ACTION: hvac_consumption_response.heating_consumption,
                              COOLING_ACTION: hvac_consumption_response.cooling_consumption,
                              FAN: hvac_consumption_response.ventilation_consumption,
                              TWO_STAGE_HEATING_ACTION: hvac_consumption_response.heating_consumption_stage_two,
                              TWO_STAGE_COOLING_ACTION: hvac_consumption_response.cooling_consumption_stage_two,
                              "UNIT": hvac_consumption_response.unit}

    return hvac_consumption_final


# Historic outdoor temperature functions
def get_outdoor_temperature_historic_stub(OUTDOOR_TEMPERATURE_HISTORICAL_HOST_ADDRESS=None,secure=True):
    """Get the stub to interact with the outdoor_temperature_historical service.

    :param OUTDOOR_TEMPERATURE_HISTORICAL_HOST_ADDRESS: Optional argument to supply host address for given service.
        Otherwise, set as environment variable.
    :return: grpc Stub object.

    """

    if OUTDOOR_TEMPERATURE_HISTORICAL_HOST_ADDRESS is None:
        OUTDOOR_TEMPERATURE_HISTORICAL_HOST_ADDRESS = os.environ["OUTDOOR_TEMPERATURE_HISTORICAL_HOST_ADDRESS"]

    if not secure:
        channel = grpc.insecure_channel(OUTDOOR_TEMPERATURE_HISTORICAL_HOST_ADDRESS)
    else:
        credentials = grpc.ssl_channel_credentials()
        channel = grpc.secure_channel(OUTDOOR_TEMPERATURE_HISTORICAL_HOST_ADDRESS, credentials)
    return outdoor_temperature_historical_pb2_grpc.OutdoorTemperatureStub(channel)


def get_raw_outdoor_temperature_historic(outdoor_historic_stub, building, start, end, window, aggregate="MEAN"):
    """Gets historic outdoor temperature as pd.series.

    :param indoor_historic_stub: grpc stub for historic outdoor temperature microservice
    :param building: (str) building name
    :param zone: (str) zone name
    :param start: (datetime timezone aware)
    :param end: (datetime timezone aware)
    :param window: (str) the interval in which to split the data.
    :return: pd.series valus=float, index=time

    """
    start = start.replace(microsecond=0)
    end = end.replace(microsecond=0)

    start_unix = int(start.timestamp() * 1e9)
    end_unix = int(end.timestamp() * 1e9)
    window_seconds = get_window_in_sec(window)

    # call service
    historic_outdoor_response = outdoor_historic_stub.GetRawTemperature(
        outdoor_temperature_historical_pb2.TemperatureRequest(
            building=building, start=int(start_unix), end=int(end_unix), window=window, aggregate=aggregate))

    # process data
    temperature_list = []
    for msg in historic_outdoor_response:
        item = {
            "datetime" : datetime.datetime.utcfromtimestamp(msg.time / 1e9).replace(tzinfo=pytz.utc).astimezone(tz=start.tzinfo),
            "temperature" : msg.temperature,
            "unit" : msg.unit
        }
        temperature_list.append(item)
    df = pd.DataFrame(temperature_list)
    df.set_index("datetime",inplace=True)
    return df

def get_preprocessed_outdoor_temperature(outdoor_historic_stub, building, start, end, window):
    """Gets historic outdoor temperature as pd.series.

    :param indoor_historic_stub: grpc stub for historic outdoor temperature microservice
    :param building: (str) building name
    :param zone: (str) zone name
    :param start: (datetime timezone aware)
    :param end: (datetime timezone aware)
    :param window: (str) the interval in which to split the data.
    :return: pd.series valus=float, index=time

    """
    start = start.replace(microsecond=0)
    end = end.replace(microsecond=0)

    start_unix = int(start.timestamp() * 1e9)
    end_unix = int(end.timestamp() * 1e9)
    window_seconds = get_window_in_sec(window)

    # call service
    historic_outdoor_response = outdoor_historic_stub.GetPreprocessedTemperature(
        outdoor_temperature_historical_pb2.TemperatureRequest(
            building=building, start=int(start_unix), end=int(end_unix), window=window))

    # process data
    temperature_list = []
    for msg in historic_outdoor_response:
        item = {
            "datetime" : datetime.datetime.utcfromtimestamp(msg.time / 1e9).replace(tzinfo=pytz.utc).astimezone(tz=start.tzinfo),
            "temperature" : msg.temperature,
            "unit" : msg.unit
        }
        temperature_list.append(item)
    df = pd.DataFrame(temperature_list)
    df.set_index("datetime",inplace=True)
    return df

# Outdoor temperature prediction functions
def get_outdoor_temperature_prediction_stub(OUTDOOR_TEMPERATURE_PREDICTION_HOST_ADDRESS=None,secure=True):
    """Get the stub to interact with the outdoor_temperature_prediction service.

    :param OUTDOOR_TEMPERATURE_PREDICTION_HOST_ADDRESS: Optional argument to supply host address for given service.
        Otherwise, set as environment variable.
    :return: grpc Stub object.

    """

    if OUTDOOR_TEMPERATURE_PREDICTION_HOST_ADDRESS is None:
        OUTDOOR_TEMPERATURE_PREDICTION_HOST_ADDRESS = os.environ["OUTDOOR_TEMPERATURE_PREDICTION_HOST_ADDRESS"]

    if not secure:
        channel = grpc.insecure_channel(OUTDOOR_TEMPERATURE_PREDICTION_HOST_ADDRESS)
    else:
        credentials = grpc.ssl_channel_credentials()
        channel = grpc.secure_channel(OUTDOOR_TEMPERATURE_PREDICTION_HOST_ADDRESS, credentials)
    return outdoor_temperature_prediction_pb2_grpc.OutdoorTemperatureStub(channel)


def get_outdoor_temperature_prediction(outdoor_prediction_stub, building, start, end, window):
    """Gets prediction outdoor temperature as pd.series.

    :param outdoor_prediction_stub: grpc stub for outdoor temperature prediction microservice
    :param building: (str) building name
    :param zone: (str) zone name
    :param start: (datetime timezone aware)
    :param end: (datetime timezone aware)
    :param window: (str) the interval in which to split the data.
    :return: pd.series valus=float, index=time

    """
    start = start.replace(microsecond=0)
    end = end.replace(microsecond=0)

    start_unix = int(start.timestamp() * 1e9)
    end_unix = int(end.timestamp() * 1e9)
    window_seconds = get_window_in_sec(window)

    # call service
    prediction_outdoor_response = outdoor_prediction_stub.GetTemperature(
        outdoor_temperature_prediction_pb2.TemperatureRequest(
            building=building, start=int(start_unix), end=int(end_unix), window=window))

    # process data
    prediction_list = []
    for msg in prediction_outdoor_response.temperatures:
        item = {
            "datetime" : datetime.datetime.utcfromtimestamp(msg.time / 1e9).replace(tzinfo=pytz.utc).astimezone(tz=start.tzinfo),
            "temperature" : msg.temperature,
            "unit" : msg.unit
        }
        prediction_list.append(item)
    df = pd.DataFrame(prediction_list)
    df.set_index("datetime",inplace=True)
    return df

def get_meter_data_historical_stub(METER_DATA_HISTORICAL_HOST_ADDRESS=None,secure=True):
    """ Get stub to interact with meter data service.
    :param METER_DATA_HISTORICAL_HOST_ADDRESS: Optional argument to supply host address for given service. Otherwise,
        set as environment variable.
    :return: grpc Stub object.
    """

    if METER_DATA_HISTORICAL_HOST_ADDRESS is None:
        METER_DATA_HISTORICAL_HOST_ADDRESS = os.environ["METER_DATA_HISTORICAL_HOST_ADDRESS"]

    if not secure:
        channel = grpc.insecure_channel(METER_DATA_HISTORICAL_HOST_ADDRESS)
    else:
        credentials = grpc.ssl_channel_credentials()
        channel = grpc.secure_channel(METER_DATA_HISTORICAL_HOST_ADDRESS,credentials)
    return meter_data_historical_pb2_grpc.MeterDataHistoricalStub(channel)


def get_meter_data_historical(meter_data_stub, bldg, start, end, point_type, aggregate, window):
    """ Get meter data as a dataframe.

    :param meter_data_stub: grpc stub for meter data service.
    :param bldg: list(str) - list of buildings.
    :param start: datetime (timezone aware)
    :param end: datetime (timezone aware)
    :param point_type: (str) Building_Electric_Meter or Green_Button_Meter
    :param aggregate: (str) Values include MEAN, MAX, MIN, COUNT, SUM and RAW (the temporal window parameter is ignored)
    :param window: (str) Size of the moving window.
    :return: pd.DataFrame(), defaultdict(list) - Meter data, dictionary that maps meter data's columns (uuid's) to sites
    """
    start = start.replace(microsecond=0)
    end = end.replace(microsecond=0)

    start_unix = int(start.timestamp() * 1e9)
    end_unix = int(end.timestamp() * 1e9)
    window_seconds = get_window_in_sec(window)

    # Create gRPC request object
    request = meter_data_historical_pb2.Request(
        building=bldg,
        start=int(start_unix),
        end=int(end_unix),
        point_type=point_type,
        aggregate=aggregate,
        window=window
    )

    historic_meter_data_response = meter_data_stub.GetMeterDataHistorical(request)

    # process data
    meter_list = []
    for msg in historic_meter_data_response:
        item = {
            "datetime" : datetime.datetime.utcfromtimestamp(msg.time / 1e9).replace(tzinfo=pytz.utc).astimezone(tz=start.tzinfo),
            "power" : msg.power
        }
        meter_list.append(item)
    df = pd.DataFrame(meter_list)
    df.set_index("datetime",inplace=True)
    return df


def get_optimizer_stub(OPTIMIZER_HOST_ADDRESS=None,secure=True):
    """ Get stub to interact with optimizer service.
    :param OPTIMIZER_HOST_ADDRESS: Optional argument to supply host address for given service. Otherwise,
        set as environment variable.
    :return: grpc Stub object.
    """

    if OPTIMIZER_HOST_ADDRESS is None:
        OPTIMIZER_HOST_ADDRESS = os.environ["OPTIMIZER_HOST_ADDRESS"]

    if not secure:
        channel = grpc.insecure_channel(OPTIMIZER_HOST_ADDRESS)
    else:
        credentials = grpc.ssl_channel_credentials()
        channel = grpc.secure_channel(OPTIMIZER_HOST_ADDRESS,credentials)
    return optimizer_pb2_grpc.OptimizerStub(channel)


def get_mpc_optimization(optimizer_stub, building, zones, start, end, window, lambda_val, starting_temperatures,
                         unit="F"):
    """Get the optimal actions according to MPC optimization.

    :param optimizer_stub: grpc stub for optimizer service
    :param building: (str) building name
    :param zones: (list str) zones names
    :param start: datetime (timezone aware)
    :param end: datetime (timezone aware)
    :param window: (str) the intervals in which to optimize
    :param lambda_val: (float) between 0 and 1. The lambda value to balance cost and discomfort.
    :param starting_temperatures: (dict) {str zone: float temperature} the starting temperatures of all zones in
        given building.
    :param unit: (string) the unit of the temperature.
    :return: (dict {(str) zone: (int) action) the optimal actions to take
    """
    start = start.replace(microsecond=0)
    end = end.replace(microsecond=0)

    start_unix = int(start.timestamp() * 1e9)
    end_unix = int(end.timestamp() * 1e9)

    # call service
    optimizer_response = optimizer_stub.GetMPCOptimization(
        optimizer_pb2.MPCOptimizationRequest(
            building=building,
            zones=zones,
            start=int(start_unix),
            end=int(end_unix),
            window=window,
            lambda_val=lambda_val,
            starting_temperatures=starting_temperatures,
            unit=unit))

    return {iter_zone: optimizer_response.actions[iter_zone] for iter_zone in zones}

def get_mpc_simulation(optimizer_stub, building, zones, start, end, window,
                        forecasting_horizon, lambda_val, starting_temperatures,
                         unit="F", num_runs=1):
    """Get the simulation results according to MPC optimization. Stops get_mpc_simulation
    when param:end is reached.

    :param optimizer_stub: grpc stub for optimizer service
    :param building: (str) building name
    :param zones: (list str) zones names
    :param start: datetime (timezone aware)
    :param end: datetime (timezone aware)
    :param window: (str) the intervals in which to optimize
    :param forecasting_horizon: (str) the timeframe for which to simulate at every step.
    :param lambda_val: (float) between 0 and 1. The lambda value to balance cost and discomfort.
    :param starting_temperatures: (dict) {str zone: float temperature} the starting temperatures of all zones in
        given building.
    :param unit: (string) the unit of the temperature.
    :param num_runs: (int) the number of runs of simulation to get a better idea
        of the variance of the simulation.
    :returns:
        actions: {iter_zone: [actions]} actions that were excecuted for
            every step.
        temperatures: ({iter_zone: [temperatures]) temperature seen
            at every step.
        len(actions[zone]) = (end - start)/window
        len(temperatures[zone]) = (end - start)/temperatures + 1
    """
    start = start.replace(microsecond=0)
    end = end.replace(microsecond=0)

    start_unix = int(start.timestamp() * 1e9)
    end_unix = int(end.timestamp() * 1e9)

    # call service
    simulation_response = optimizer_stub.GetMPCSimulation(
        optimizer_pb2.SimulationRequest(
            building=building,
            zones=zones,
            start=int(start_unix),
            end=int(end_unix),
            window=window,
            forecasting_horizon=forecasting_horizon,
            lambda_val=lambda_val,
            starting_temperatures=starting_temperatures,
            unit=unit,
            num_runs=num_runs))


    actions = []
    temperatures = []
    for simulation_result in simulation_response.simulation_results:
        actions.append({iter_zone: simulation_result.actions[iter_zone] for iter_zone in zones})
        temperatures.append({iter_zone: simulation_result.temperatures[iter_zone] for iter_zone in zones})

    return actions, temperatures


def check_data(data, start, end, window, check_nan=False):
    """Checks if data has right times and optionally checks for nan.
    This includes checking that the daterange [param:start (inculsive) - param:end (exclusive)) is included in the data.
    And that the time-difference between datapoints equals to param:window.

    :param data: pd.df or pd.series
    :param start: datetime (timezone aware)
    :param end: datetime (timezone aware)
    :param window: (string)
    :param check_nan: If False (default) will not return an error if a datapoint is Nan. If True, will error on nan
    data points.
    :return: str err message. If no error, returns None."""
    if not isinstance(data, pd.DataFrame) and not isinstance(data, pd.Series):
        return "Is not a pd.DataFrame/pd.Series"

    window = get_window_in_sec(window)
    time_diffs = data.index.to_series(keep_tz=True).diff()
    if (time_diffs.shape[0] > 1) and ((time_diffs.min() != time_diffs.max()) or (time_diffs.min().seconds != window)):
        return "Missing rows or/and bad time frequency."
    if (start not in data.index) or ((end - datetime.timedelta(seconds=window)) not in data.index):
        return "Does not have valid start or/and end time."
    if check_nan and (data.isna().values.any()):
        return "Nan values in data."
    return None

def get_baseline_optimizer_stub(BASELINE_OPTIMIZER_HOST_ADDRESS=None,secure=True):
    """ Get stub to interact with optimizer service.
    :param BASELINE_OPTIMIZER_HOST_ADDRESS: Optional argument to supply host address for given service. Otherwise,
        set as environment variable.
    :return: grpc Stub object.
    """

    if BASELINE_OPTIMIZER_HOST_ADDRESS is None:
        BASELINE_OPTIMIZER_HOST_ADDRESS = os.environ["BASELINE_OPTIMIZER_HOST_ADDRESS"]

    if not secure:
        channel = grpc.insecure_channel(BASELINE_OPTIMIZER_HOST_ADDRESS)
    else:
        credentials = grpc.ssl_channel_credentials()
        channel = grpc.secure_channel(BASELINE_OPTIMIZER_HOST_ADDRESS,credentials)
    return baseline_optimizer_pb2_grpc.BaselineOptimizerStub(channel)

def get_normal_schedule_action(baseline_optimizer_stub,building,zones,start,end,window,starting_temperatures,unit,occupancy,do_not_exceed):
    start = start.replace(microsecond=0)
    end = end.replace(microsecond=0)

    start_unix = int(start.timestamp() * 1e9)
    end_unix = int(end.timestamp() * 1e9)

    baseline_optimizer_response = baseline_optimizer_stub.GetNormalScheduleAction(baseline_optimizer_pb2.NormalScheduleRequest(building=building,zones=zones,start=start_unix,end=end_unix,window=window,starting_temperatures=starting_temperatures,unit=unit,occupancy=occupancy,do_not_exceed=do_not_exceed))
    return baseline_optimizer_response.actions

def get_setpoint_expansion_action(baseline_optimizer_stub,building,zones,start,end,window,starting_temperatures,unit,occupancy,do_not_exceed,expansion_degrees):
    start = start.replace(microsecond=0)
    end = end.replace(microsecond=0)

    start_unix = int(start.timestamp() * 1e9)
    end_unix = int(end.timestamp() * 1e9)

    baseline_optimizer_response = baseline_optimizer_stub.GetSetpointExpansionAction(baseline_optimizer_pb2.SetpointExpansionRequest(building=building,zones=zones,start=start_unix,end=end_unix,window=window,starting_temperatures=starting_temperatures,unit=unit,occupancy=occupancy,do_not_exceed=do_not_exceed,expansion_degrees=expansion_degrees))
    return baseline_optimizer_response.actions

def get_demand_charge_action(baseline_optimizer_stub,building,zones,start,end,window,starting_temperatures,unit,occupancy,do_not_exceed,max_zones,include_all_zones):
    start = start.replace(microsecond=0)
    end = end.replace(microsecond=0)

    start_unix = int(start.timestamp() * 1e9)
    end_unix = int(end.timestamp() * 1e9)

    baseline_optimizer_response = baseline_optimizer_stub.GetDemandChargeAction(baseline_optimizer_pb2.DemandChargeRequest(building=building,zones=zones,start=start_unix,end=end_unix,window=window,starting_temperatures=starting_temperatures,unit=unit,occupancy=occupancy,do_not_exceed=do_not_exceed,max_zones=max_zones,include_all_zones=include_all_zones))
    return baseline_optimizer_response.actions

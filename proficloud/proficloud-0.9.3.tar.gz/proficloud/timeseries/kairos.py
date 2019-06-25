import requests
import json
from .proficloudutil import *
import pandas

class KairosConnector():
    """
    This class provides a connection to a KairosDb REST API.
    Metrics can be queried and outputted to convenient formats for machine learning.
    Sub-Classes for the different services such as TSD and EWIMA exist.

    :type url: str
    :param url: base url for kairos REST API
    :type headers: dict
    :param headers: Headers for the REST call. See requests documentation for more info (default=False)
    :type trustEnvironment: boolean
    :param trustEnvironment: choose to trust the environment, e.g. load proxy settings. (Default: False)
    :type disableSSLVerification: boolean
    :param disableSSLVerification: Disable SSL Verification. Useful when behind SSL proxy. Only disable verification if there is no other option!
    :type proxies: dict
    :param proxies: Proxy information. Default: None. Example value: {"http": "http://127.0.0.1:3128", "https": "http://127.0.0.1:3128"} This will force trustEnvironment to False.
    """

    DEBUGTIME = False
    """Debug request response times (print)"""
    DEBUGRESPONSE = False
    """
    Debug http-responses. When set to true, the attribute DEBUGRESPONSECONTENT then contains the last raw response. 
    Does not work when calling API in parallel using the same instance!
    """
    DEBUGRESPONSECONTENT = None
    """
    Contains the last response if DEBUGRESPONSE is set to True.
    """
    DEBUGPAYLOAD = False
    """ DoThis """
    DEBUGPAYLOADCONTENT = None
    """ DoThis """

    datetimeformat = "%Y-%m-%d %H:%M:%S.%f"
    """Expected Datetime-format. Default: '%Y-%m-%d %H:%M:%S.%f' """
    
    def __init__(self, url, headers, trustEnvironment=False, disableSSLVerification=False, tags=None, proxies = None):

        self.session = requests.Session()
        """The requests-session for communication through REST"""

        self.session.trust_env = trustEnvironment #(disable proxy when false, as it is always sourced from /etc/environment; (if available))
        self.session.verify = not disableSSLVerification
        if proxies is not None:
            self.session.trust_env = False
            self.session.proxies.update(proxies)
        
        self.headers = headers
        """The headers for the REST communication"""
        self.tags = tags
        """The tags to add to the Kairosdb API calls"""
        
    
    #def listMetrics(self, prefix=None):
    #    """
    #    List available metrics. This does not work at the moment as this API functionality is locked.
    #
    #    :type prefix: str
    #    :param prefix: The prefix to filter metrics.
    #    """
    #
    #    if prefix == None:
    #        response = self.session.get(url=self.url+"api/v1/metricnames", headers=self.headers)
    #    else:
    #        response = self.session.get(url=self.url+"api/v1/metricnames?prefix="+prefix, headers=self.headers)
    #
    #    if self.DEBUGRESPONSE:
    #        self.DEBUGRESPONSECONTENT = response
    #
    #    return response
    
    #def getDbVersion(self):
    #    response = self.session.get(url=self.url+"api/v1/version", headers=self.headers)
    # 
    #    if self.DEBUGRESPONSE:
    #        self.DEBUGRESPONSECONTENT = response
    #    return response

    def __query(self, payload):
        """
        Send a query to the kairosdb.
        
        :type payload: dict
        :param payload: The payload (will be serialized to json)
        :return: returns deserialized response content. Error handling is todo!
        :rtype: dict
        """
        if self.DEBUGTIME:
            start_t = datetime.datetime.now()

        try:
            response = self.session.post(url=self.url+"api/v1/datapoints/query/", headers=self.headers, data=json.dumps(payload))
        except:
            raise

        if response.status_code != 200:
            if response.status_code == 504:
                raise requests.exceptions.HTTPError("Query unsuccessful. The query response exceeds the maxium allowed quota for this API. Try decreasing the time range or use aggregators!")
            else:
                raise requests.exceptions.HTTPError("Query unsuccessful. Response:"+str(response.status_code)+"; "+str(response.content))

        if self.DEBUGTIME:
            end_t = datetime.datetime.now()
            print("API call took " + str(end_t - start_t))
            start_t = datetime.datetime.now()

        js = json.loads(response.content)
        if self.DEBUGTIME:
            end_t = datetime.datetime.now()
            print("JSON deserialization took "+str(end_t - start_t))

        if self.DEBUGRESPONSE:
            self.DEBUGRESPONSECONTENT = response

        return js
    
    def queryMetrics(self, metrics, start_absolute=None, start_relative=None, end_absolute=None, end_relative=None, limit=None, aggregators=None, createDf=True, fillNaMethod = None, dropTrailingNa=True, orderDesc=False, convertTimestamp=False):
        """
        Query metrics and return the data as pandas DataFrame.
        You must specify either start_absolute or start_relative but not both. Similarly, you may specify either end_absolute or end_relative but not both. If either end time is not specified the current date and time is assumed.

        :type metrics: list(str), str
        :param metrics: A list of metric names (or a single metric name) to query. 
        :type start_absolute: int, datetime, str or None
        :param start_absolute: Timestamp (ms based), or datetime object (or datetime as string) not used when None. (Default: None)
        :type start_relative: dict
        :param start_relative: The relative start time is the current date and time minus the specified value and unit. Possible unit values are “milliseconds”, “seconds”, “minutes”, “hours”, “days”, “weeks”, “months”, and “years”. For example, if the start time is 5 minutes, the query will return all matching data points for the last 5 minutes. Example value: { "value": "10", "unit": "minutes" } (Default: None)
        :type end_absolute: int, datetime, str or None
        :param end_absolute: Timestamp (ms based), or datetime object (or datetime as string). This must be later in time than the start time. If not specified, the end time is assumed to be the current date and time. (Default: None)
        :type end_relative: dict
        :param end_relative: The relative end time is the current date and time minus the specified value and unit. Possible unit values are “milliseconds”, “seconds”, “minutes”, “hours”, “days”, “weeks”, “months”, and “years”. For example, if the start time is 30 minutes and the end time is 10 minutes, the query returns matching data points that occurred between the last 30 minutes up to and including the last 10 minutes. If not specified, the end time is assumed to the current date and time. Example value: { "value": "10", "unit": "minutes" } (Default: None)
        :type limit: int or None
        :param limit: Limits the number of data points returned from the data store (for each metric). (Default: None)
        :type orderDesc: boolean
        :param orderDesc: Orders returned data points based on timestamp. Descending order when True, or ascending when False (default) Only in effect when returning DataFrame.
        :type createDF: boolean
        :param createDF: Convert response into a convenient Pandas Dataframe. (Default=True)
        :type fillNaMethod: str
        :param fillNaMethod: {‘backfill’, ‘bfill’, ‘pad’, ‘ffill’, None}, default None. Method to use for filling holes in reindexed Series pad / ffill: propagate last valid observation forward to next valid backfill / bfill: use NEXT valid observation to fill gap
        :type dropTrailingNa: boolean
        :param dropTrailingNa: Drop trailing NaN values when set to true. Especially useful when end neither end param is specified (filters time delay when querying multiple metrics). Default: True
        :type convertTimestamp: boolean
        :param convertTimestamp: Convert the timestamp to datetime (Default: False)
        :type aggregators: dict
        :param aggregators: This is an ordered array of aggregators. They are processed in the order specified. The output of an aggregator is passed to the input of the next until all have been processed. Aggregators are performed on all metrics. This is a simplification over Kairos to allow table conversion. See https://kairosdb.github.io/docs/build/html/restapi/Aggregators.html for information on them.
        :rtype: pandas.DataFrame or dict
        :return: Returns pandas.DataFrame 
        """

        if self.DEBUGTIME:
            start_t = datetime.datetime.now()

        payload = {}

        if(start_absolute != None):
            payload["start_absolute"] = datetimeToTimestampMs(start_absolute)
        elif(start_relative != None):
            payload["start_relative"]= start_relative
        elif(start_absolute == None and start_relative == None):
            payload["start_absolute"] = datetimeToTimestampMs(datetime.datetime.now())

        if(end_absolute != None):
            payload["end_absolute"] = datetimeToTimestampMs(end_absolute)
        elif(end_relative != None):
            payload["end_relative"] = end_relative
        elif(end_absolute == None and end_relative == None):
            payload["end_absolute"] = datetimeToTimestampMs(datetime.datetime.now())
        
        payload["time_zone"] = "UTC"

        if(isinstance(metrics, str)):
            metrics = [metrics]    
        
        if(isinstance(aggregators, dict)):
            aggregators = [aggregators]

        ml = []
        data = []
        for m in metrics:
            ml = []
            mdict = {}
            mdict["name"] = [ m ]
            if limit is not None:
                mdict["limit"] = limit
            if aggregators is not None:
                mdict["aggregators"] = aggregators
            #This has no effect. Why? Bug in Kairos? --> Order in Dataframe
            #if orderDesc:
            #    mdict["order"] = "desc" 

            ml.append(mdict)
                
            payload["metrics"] = ml

            if self.DEBUGTIME:
                end_t = datetime.datetime.now()
                print("Payload construction took "+str(end_t - start_t))

            if self.DEBUGPAYLOAD:
                self.DEBUGPAYLOADCONTENT = payload

            datametric = self.__query(payload)
            data.append(datametric)

        if not createDf:
            return data
        else:
            if self.DEBUGTIME:
                start_t = datetime.datetime.now()
            dfres = pandasDfFromQueryResponse(data, fillNaMethod=fillNaMethod, dropTrailingNa=dropTrailingNa, convertTimestamp=convertTimestamp, orderDesc=orderDesc)
            if self.DEBUGTIME:
                end_t = datetime.datetime.now()
                print("Dataframe conversion took "+str(end_t - start_t))
            return dfres

    def __add(self, payload):
        """
        Add metrics payload to the kairosdb.
        
        :type payload: dict
        :param payload: The payload (will be serialized to json)
        :rtype: boolean
        :return: True on success, False otherwise
        """
        if self.DEBUGTIME:
            start_t = datetime.datetime.now()

        try:
            response = self.session.post(url=self.url+"api/v1/datapoints/write", headers=self.headers, data=json.dumps(payload))
        except:
            raise

        if self.DEBUGTIME:
            end_t = datetime.datetime.now()
            print("API call took " + str(end_t - start_t))

        if self.DEBUGRESPONSE:
            self.DEBUGRESPONSECONTENT = response

        #add returns 204 with no body on success
        if response.status_code == 204:
            return True
        else:
            return False


    def addMetrics(self, metricnames, metricvalues, timestamp=None):
        """
        Add new metric values with timestamp. By default, the system UTC time is used.

        :type metricnames: List of strings
        :param metricnames: List of metric names to write. Corresponding values are placed in metricvalues param.
        :type metricvalues: List of numbers
        :param metricvalues: List of values to write. Corresponding metric names are palced in metricnames param.
        :type timestamp: datetime, date-string, float or int
        :param timestamp: Millisecond based timestamp. Default is None, which results in the use of systems current utc time.
        :rtype: boolean
        :return: True on success, False otherwise
        """

        if metricnames is str:
            metricnames = [metricnames]
        
        if len(metricnames) != len(metricvalues):
            raise Exception("Metricnames and Metricvalue are not same length.") 

        now = datetime.datetime.utcnow()
        nowMs = datetimeToTimestampMs(now)
        if timestamp is not None:
            nowMs = datetimeToTimestampMs(timestamp)

        payload = []
        for i in range(len(metricnames)):
            metric = {}
            metric["name"] = metricnames[i]
            metric["timestamp"] = nowMs
            metric["value"] = metricvalues[i]    
            if self.tags is not None:
                metric["tags"] = self.tags

            payload = payload + [metric]

        result = self.__add(payload)
        return result

    def addMetricsBatch(self, dataframe, timestampColumnName="Timestamp"):
        """
        Send batch metrics to. This takes a pandas dataframe (which must contain a column to use as a timestamp) and transfers all of its contents at once.

        :type dataframe: pandas.core.frame.DataFrame
        :param dataframe: The dataframe to send to the cloud
        :type timestampColumnName: string
        :param timestampColumnName: The name of the timestamp column.
        """

        if type(dataframe) is not pandas.core.frame.DataFrame:
            raise TypeError("dataframe is not a Pandas DataFrame.")
        if timestampColumnName not in dataframe.columns:
            raise KeyError("dataframe does not contain \""+timestampColumnName+"\"  column.")

        payload = []

        times = dataframe[timestampColumnName].map(datetimeToTimestampMs).values

        for column in dataframe.columns:
            if column == timestampColumnName:
                continue
            
            metric = {}
            metric["name"] = column
      
            points = dataframe[column].values
            metric["datapoints"] = []
            #[timestamp, value]
            for i in range(len(times)):
                metric["datapoints"].append([times[i].item(), points[i].item()])

            if self.tags is not None:
                metric["tags"] = self.tags

            payload.append(metric)

        result = self.__add(payload)
        return result

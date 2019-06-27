
import os
import pandas as pd
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import utils.utils as utils
from typing import Dict
from utils.graph_utils import GraphUtils
#!pip install -U -q PyDrive emoji
import emoji

class MetricGenerator:
    """
    Contains helper methods for generating metrics from Splunk data
    """
    def __init__(self, platform: str, prev_release: str, curr_release: str):
        """
        Init code
        """
        self.platform = platform
        self.last_release = prev_release
        self.this_release = curr_release
        self.graph_utils = GraphUtils(prev_release, curr_release)

    
    def generate_bootstrap_metric(self, bootstrap_raw: object, ept_threshold: int, outliers_time: int, sla_threshold: int):
      """
      Lists bootstrap EPT by app version and Wifi network. Generates a boxplot from data and verifies if the SLA is satisfied
      
      Args:
        bootstrap_raw (object): Raw bootsrap data.
        ept_threshold (int): Threshold value for EPT.
        outliers_time (int): Threshold time to remove percentage outliers (in seconds).
        sla_threshold (int): Threshold value for verifying SLA.
      """
      try:
        datasource = bootstrap_raw[bootstrap_raw['EPT'] < ept_threshold] #Removing unreasonable outliers
        wifi_datasource = datasource[datasource['network'] == 'Wifi']

        self.aggregate_by_network_appver(bootstrap_raw, ept_threshold, outliers_time)
        if self.platform.lower() == "ios":
          self.graph_utils.visualize_using_boxplot(wifi_datasource, 1, sla_threshold, 5000)
        else:
          self.graph_utils.visualize_using_boxplot(wifi_datasource, 1, sla_threshold, None)
        
        v = [str(self.last_release), str(self.this_release)] # `v` is a sorted (older -> newer) list of app Versions.
        p = ['#00a1e0ff', '#7c868dff', '#00b2a9ff', '#963cbdff']
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12,8))
        sns.distplot(wifi_datasource[wifi_datasource['appVersion']==self.this_release]['EPT'], color=p[0], ax=ax, label=str(self.this_release))
        plt.legend()
        ax.set_title('Wifi Bootstrap EPT')
        plt.show()

        #Verify SLA
        self.verify_sla(wifi_datasource, sla_threshold)
      except Exception as e:
        print("generate_bootstrap_metric():: Error generating bootstrap metric: ", e)

    
    def generate_object_home_metric(self, objecthome_raw: object, ept_threshold: int, outliers_time: int, sla_threshold: int):
      """
      Lists object home EPT by app version and Wifi network. Generates a boxplot from data and verifies if the SLA is satisfied
      
      Args:
        objecthome_raw (object): Raw object home data.
        ept_threshold (int): Threshold value for EPT.
        outliers_time (int): Threshold time to remove percentage outliers (in seconds).
        sla_threshold (int): Threshold value for verifying SLA.
      """
      try:
        datasource = objecthome_raw[objecthome_raw['EPT'] < ept_threshold] #Removing unreasonable outliers
        wifi_datasource = datasource[datasource['network'] == 'Wifi']

        self.aggregate_by_network_appver(objecthome_raw, ept_threshold, outliers_time)
        data = objecthome_raw.groupby(['appVersion', 'network', 'entitytype']).apply(utils.my_agg)
        print(data)
        print(self.platform)
        if self.platform.lower() == "ios":
          self.graph_utils.visualize_using_boxplot(wifi_datasource[wifi_datasource['EPT'] < 5000], 2 ,sla_threshold, 4000)
        else:
          self.graph_utils.visualize_using_boxplot(wifi_datasource, 2, sla_threshold, None)

        #Verify SLA
        self.verify_sla(wifi_datasource, sla_threshold)

        #verify SLA for each entitytype
        self.verify_sla_for_entitytype(wifi_datasource, sla_threshold)
      except Exception as e:
        print("generate_object_home_metric():: Error generating object home metric: ", e)
    
    def generate_rh_cold_metric(self, rh_cold: object, ept_threshold: int, outliers_time: int):
      """
      Lists rh cold EPT by app version and Wifi network. Generates a boxplot from data
      
      Args:
        rh_cold (object): Raw record home cold data.
        ept_threshold (int): Threshold value for EPT.
        outliers_time (int): Threshold time to remove percentage outliers (in seconds).
      """
      try:
        self.__generate_record_home_metric("cold", rh_cold, ept_threshold, outliers_time, 2750, 7000)
      except Exception as e:
        print("generate_rh_cold_metric():: Error generating record home cold metric: ", e)
    
    def generate_rh_warm_metric(self, rh_warm: object, ept_threshold: int, outliers_time: int):
      """
      Lists rh warm EPT by app version and Wifi network. Generates a boxplot from data
      
      Args:
        rh_warm (object): Raw record home warm data.
        ept_threshold (int): Threshold value for EPT.
        outliers_time (int): Threshold time to remove percentage outliers (in seconds).
      """
      try:
        self.__generate_record_home_metric("warm", rh_warm, ept_threshold, outliers_time, 1750, 5000)
      except Exception as e:
        print("generate_rh_warm_metric():: Error generating record home warm metric: ", e)
    
    def __generate_record_home_metric(self, type: str, rh_data: object, ept_threshold: int, outliers_time: int, release_criteria: int, ylimit: int):
      """
      Lists home EPT by app version and Wifi network. Generates a boxplot from data
      
      Args:
        rh_data (object): Raw record home cold / warm data.
        ept_threshold (int): Threshold value for EPT.
        outliers_time (int): Threshold time to remove percentage outliers (in seconds).
      """
      try:
        datasource = rh_data[rh_data['EPT'] < ept_threshold] #Removing unreasonable outliers
        wifi_datasource = datasource[datasource['network'] == 'Wifi']

        data = rh_data.groupby(['appVersion', 'network', 'entitytype']).apply(utils.my_agg)
        print(data)
        
        self.aggregate_by_network_appver(rh_data, ept_threshold, outliers_time)

        if self.platform.lower() == "ios":
          self.graph_utils.visualize_using_boxplot(wifi_datasource, 2, release_criteria, ylimit)
        elif self.platform.lower() == "android":
          if type == "warm":
            self.graph_utils.visualize_using_boxplot(wifi_datasource, 2, 2750, None)
          else:
            #cold
            self.graph_utils.visualize_using_boxplot(wifi_datasource, 2, 3750, None)
      except Exception as e:
        print("generate_record_home_metric():: Error generating record home metric: ", e)

    def generate_mainfeed_metric(self, feeds_raw: object, ept_threshold: int, outliers_time: int, sla_threshold: int):
      """
      Lists main feed EPT by app version and Wifi network. Generates a boxplot from data and verifies if the SLA is satisfied
      
      Args:
        feeds_raw (object): Raw main feed data.
        ept_threshold (int): Threshold value for EPT.
        outliers_time (int): Threshold time to remove percentage outliers (in seconds).
        sla_threshold (int): Threshold value for verifying SLA.
      """
      try:
        datasource = feeds_raw[feeds_raw['EPT'] < ept_threshold] #Removing unreasonable outliers
        wifi_datasource = datasource[datasource['network'] == 'Wifi']

        self.aggregate_by_network_appver(feeds_raw, ept_threshold, outliers_time)
        if self.platform.lower() == "ios":
          self.graph_utils.visualize_using_boxplot(wifi_datasource, 1, sla_threshold, 4000)
        else:
          self.graph_utils.visualize_using_boxplot(wifi_datasource, 1, sla_threshold, None)
        
        #Verify SLA
        self.verify_sla(wifi_datasource, sla_threshold)
      except Exception as e:
        print("generate_mainfeed_metric():: Error generating main feed metric: ", e)

    
    def generate_cold_start_metric(self, coldstart_raw: object, ept_threshold: int, outliers_time: int, sla_threshold: int):
      """
      Lists cold start EPT by app version and Wifi network. Generates a boxplot from data and verifies if the SLA is satisfied
      
      Args:
        coldstart_raw (object): Raw cold start data.
        ept_threshold (int): Threshold value for EPT.
        outliers_time (int): Threshold time to remove percentage outliers (in seconds).
        sla_threshold (int): Threshold value for verifying SLA.
      """
      try:
        datasource = coldstart_raw[coldstart_raw['EPT'] < ept_threshold] #Removing unreasonable outliers
        wifi_datasource = datasource[datasource['network'] == 'Wifi']

        self.aggregate_by_fields(coldstart_raw, ept_threshold, outliers_time, ['appVersion', 'releaseVersion', 'network'])
        if self.platform.lower() == "ios":
          self.graph_utils.visualize_using_boxplot(wifi_datasource, 1, sla_threshold, 5000)
        else:
          self.graph_utils.visualize_using_boxplot(wifi_datasource, 1, sla_threshold, None)

        #Verify SLA
        self.verify_sla(wifi_datasource, sla_threshold)
      except Exception as e:
        print("generate_cold_start_metric():: Error generating cold start metric: ", e)

    
    def generate_app_start_metric(self, appstartup_raw: object, ept_threshold: int, outliers_time: int, sla_threshold: int):
      """
      Lists app start EPT by app version and Wifi network. Generates a boxplot from data and verifies if the SLA is satisfied
      
      Args:
        appstartup_raw (object): Raw bootsrap data.
        ept_threshold (int): Threshold value for EPT.
        outliers_time (int): Threshold time to remove percentage outliers (in seconds).
        sla_threshold (int): Threshold value for verifying SLA.
      """
      try:
        datasource = appstartup_raw[appstartup_raw['EPT'] < ept_threshold] #Removing unreasonable outliers
        wifi_datasource = datasource[datasource['network'] == 'Wifi']

        self.aggregate_by_fields(appstartup_raw, ept_threshold, outliers_time, ['appVersion', 'releaseVersion', 'network', 'startupFlow'])
        if self.platform.lower() == "ios":
          self.graph_utils.visualize_using_boxplot(wifi_datasource, 1, sla_threshold, 5000)
        else:
          self.graph_utils.visualize_using_boxplot(wifi_datasource, 1, sla_threshold, None)

        #Verify SLA
        self.verify_sla(wifi_datasource, sla_threshold)
      except Exception as e:
        print("generate_app_start_metric():: Error generating app startup metric: ", e)

    
    def aggregate_by_network_appver(self, raw_datasource: object, ept_threshold: int, outliers_time: int):
      """
      Groups EPT data by app version and Wifi network and generates percentile EPT (P50 and P95)

      Args:
        raw_datasource (object): Raw datasource upon which aggregation is to be applied.
        ept_threshold (int): Threshold value for EPT.
        outliers_time (int): Threshold time to remove percentage outliers (in seconds).
      """
      try:
        datasource = raw_datasource[raw_datasource['EPT'] < ept_threshold] #Removing unreasonable bootstrap outliers
        print("Percentage Of Outliers over {outliers_time} secs (%): ".format(**vars()), (len(raw_datasource) - len(datasource))/len(raw_datasource) * 100)

        print("\n\n\n\t EPT (ms) \n")
        b = raw_datasource.groupby(['appVersion','network']).apply(utils.my_agg)
        print(b)
      except Exception as e:
        print("aggregate_by_network_appver():: Error aggregating by network & app version: ", e)


    def aggregate_by_fields(self, raw_datasource: object, ept_threshold: int, outliers_time: int, groupby_fields: []):
      """
      Aggregate the data by given fields

      Args:
        raw_datasource (object): Raw datasource upon which aggregation is to be applied.
        ept_threshold (int): Threshold value for EPT.
        outliers_time (int): Threshold time to remove percentage outliers (in seconds).
        groupby_fields (:obj:`list` of :obj:`str`): List of fields to be used for group by.
      """
      try:
        datasource = raw_datasource[raw_datasource['EPT'] < ept_threshold] #Removing unreasonable bootstrap outliers
        print("Percentage Of Outliers over {outliers_time} secs (%): ".format(**vars()), (len(raw_datasource) - len(datasource))/len(raw_datasource) * 100)

        print("\n\n\n\t EPT (ms) \n")
        b = raw_datasource.groupby(groupby_fields).apply(utils.my_agg)
        print(b)
      except Exception as e:
        print("aggregate_by_fields():: Error aggregating by given fields: ", e)


    def verify_sla(self, wifi_datasource: object, sla_threshold: int):
      """
      Verifies if SLA requirement is met

      Args:
        wifi_datasource (object): Wifi datasource to be used for SLA verification.
        sla_threshold (int): Threshold value for SLA.
      """
      try:
        datasource_p95 = wifi_datasource[wifi_datasource['appVersion']==self.this_release]['EPT'].quantile(q=0.95)
        print("SLA: P95 < {sla_threshold} ms".format(**vars()))
        print(datasource_p95)
        if datasource_p95 < sla_threshold:
          print(emoji.emojize(':white_check_mark: PASS - EPT PERC95 < {sla_threshold} ms on WiFi network in Perf Lab Env'.format(**vars()), use_aliases=True))
        else:
          print(emoji.emojize(':no_entry: FAIL - EPT PERC95 < {sla_threshold} ms on WiFi network in Perf Lab Env'.format(**vars()), use_aliases=True))
      except Exception as e:
        print("verify_sla():: Error verifying SLA: ", e)

    def verify_sla_for_entitytype(self, wifi_datasource: object, sla_threshold: int):
      """
      Verifies if SLA requirement for each entitytype is met

      Args:
        wifi_datasource (object): Wifi datasource to be used for SLA verification.
        sla_threshold (int): Threshold value for SLA.
      """
      try:
        current_release = wifi_datasource[wifi_datasource['appVersion']==self.this_release]
        object_p95 = current_release.groupby('entitytype')
        print("SLA: Native OH P95 < {sla_threshold} ms".format(**vars()))
        for entity, group in object_p95:
          if group.quantile(q=0.95)['EPT'] < sla_threshold:
            print(emoji.emojize(':white_check_mark: Native EPT for {0}'.format(entity), use_aliases=True))
          else:
            print(emoji.emojize(':no_entry: Native EPT for {0}'.format(entity), use_aliases=True))
      except Exception as e:
        print("verify_sla_for_entitytype():: Error verifying SLA for entitytype: ", e)



    def load_data_from_folder(self, folder_path: str) -> Dict[str, object]:
      """
      Loads data from given folder into dictonary object

      Args:
        folder_path (str): Path of the folder/directory where Splunk csv files are stored.

      Returns:  
        Dict[str, object]: Returns a dictonary containing key-data as key-value pairs
      """
      extension = ".csv"
      raw_data = dict()
      try:

        #if given path exists and is a directory/folder then execute following code
        if not os.path.isdir(folder_path):
          print ("%s path doesnot exists or is not a directory/folder."%folder_path)
          return {}

        #Bootstrap
        raw_data["Bootstrap"] = self.__load_raw_data_from_folder(folder_path, extension, '_Bootstrap')

        #Object Home
        raw_data["OH"] = self.__load_raw_data_from_folder(folder_path, extension, '_OH')

        #Record Home
        recordhome_raw = self.__load_raw_data_from_folder(folder_path, extension, '_RH')
        if not recordhome_raw is None:
          raw_data["RH_Cold"] = recordhome_raw[recordhome_raw['isWarmRecord']==False]
          raw_data["RH_Warm"] = recordhome_raw[recordhome_raw['isWarmRecord']==True]

        #Native Main Feed
        raw_data["MainFeed"] = self.__load_raw_data_from_folder(folder_path, extension, '_MainFeed')
        
        #Cold Start
        raw_data["ColdStart"] = self.__load_raw_data_from_folder(folder_path, extension, '_ColdStart')
        
        #App Startup
        raw_data["AppStart"] = self.__load_raw_data_from_folder(folder_path, extension, '_AppStartup')
      except Exception as e:
        print("load_data_from_folder():: Error while loading splunk data from folder: ", e)
      return raw_data

    def __load_raw_data_from_folder(self, folder_path: str, extension: str, keyword: str) -> Dict[str, object]:
      datasource = utils.search_for_file(folder_path, extension, keyword)
      if (datasource is None) or (len(datasource) == 0):
        print("%s data file not found." %keyword)  
        return None
      elif len(datasource) > 0:
        return utils.load_file(folder_path, datasource)

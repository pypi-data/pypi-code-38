import glob, os
import pandas as pd
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials
import IPython
import plotly
import plotly.graph_objs as go

def my_agg(datatype: object):
  """
  Aggregate function 

  Args:
        datatype (object): Object on which aggregation is to be applied.
  """
  names = {
          '# of Events' : pd.to_numeric(datatype['appVersion'].count()),
          'P50': datatype['EPT'].quantile(q=0.50),
          'P95': datatype['EPT'].quantile(q=0.95)} 
  return pd.Series(names, index=['# of Events', 'P50', 'P95'])

def aggregate_all_quantiles_mem(datatype: object):
  names = {
        'P25': datatype['usedMemory'].quantile(q=0.25),
        'P50': datatype['usedMemory'].quantile(q=0.50),
        'P75': datatype['usedMemory'].quantile(q=0.75),
        'P95': datatype['usedMemory'].quantile(q=0.95)}
  return pd.Series(names, index=['P25', 'P50', 'P75', 'P95'])

def search_for_file(search_path: str, extension: str, keyword: str) -> str:
  """
  Seraches given path for a filename containing specified keyword
  and returns the file path if file found else returns None 

  Args:
        search_path (str): Directory/folder path to serach for Splunk data files
        extension (str): Extension of data file with `.` E.g. `.csv`
        keyword (str): Keyword string to lookup in the filename.
  
  Returns:  
        str: Returns a the filename if file with given keyword is found
  """
  try:
    os.chdir(search_path)
    for file in glob.glob("*" + extension):
      if(file.lower().find(keyword.lower()) > 0):
        return file
  except Exception as e:
        print("search_for_file():: Error in searching for file: ", e)
  return None


def load_file(folder_path: str, filename: str):
  """
  Given the folder path and filename reads the file into a dataframe

  Args:
        folder_path (str): Directory/folder path where the given file is stored
        filename (str): Name of the file where splunk data is stored.
  """
  try:
    file = pd.read_csv(folder_path + "/" + filename, parse_dates=['_time'], index_col='_time', header=0)
  except FileNotFoundError:
      raise FileNotFoundError('File not found')
  except Exception as e:
      print("Error in reading file: ", e)
  return file

def load_from_folder(folder_id, filename: str, drive):
  
  # First, lookup the folder.
  q="name='{}' and mimeType = 'application/vnd.google-apps.folder'"
  
  # Auto-iterate through all files in the root folder.
  file_list = drive.ListFile({'q': "'{0}' in parents and trashed=false".format(folder_id)}).GetList()
  for file1 in file_list:
    #print('title: %s, id: %s' % (file1['title'], file1['id']))
    if file1['title'] == filename:
      downloaded = drive.CreateFile({'id': file1['id']})
      print('title: %s, mimeType: %s' % (downloaded['title'], downloaded['mimeType']))
      downloaded.GetContentFile('/tmp/data.csv', downloaded['mimeType'])
      print('download COMPLETE')

      # Convert to a DataFrame and render.
      x = pd.read_csv('/tmp/data.csv', parse_dates=['_time'], index_col='_time', header=0)
      return x
  raise KeyError


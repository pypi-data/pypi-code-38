# core python libaries
from shutil import disk_usage
from sys import argv
from os.path import exists
from os import mkdir
from csv import DictWriter
from threading import Thread
# 3rd party files
from requests import request
import pandas

#TODO
# add next steps

class Bytez:
  def __init__( self, **kwargs ):
    for attribute in kwargs:
      if hasattr( self, attribute ) is False:
        self.__dict__[ attribute ] = kwargs[ attribute ]

    if hasattr( self, 'token' ) is False:
      self.token = self.auth()

    self.endpoint = f'https://api.bytez.io/users/v1/{self.user}/repos'

  # return a JWT
  def auth(self):
    try:
      self.token = None
      json = self.request( method='post', url='https://api.bytez.io/auth', body = self.creds)
      if 'error' in json:
        raise Exception('Bytez: unauthorized - double check your email and secret')
      self.token = { 'Authorization': 'Bearer ' + json['token'] };
      print('Bytez: connected')
      return self.token
    except IOError:
      print('Bytez: error - could not connect to servers')
    except Exception as error:
      print( error )
    print('Bytez: connection destroyed')

  # get containers
  def containers(self):
    json = self.request( url = self.endpoint )
    return [ container['repo'] for container in json.values() ];

  # get single container
  def container(self, title): return Container( self, title );
  def request(self, url, method = 'get', params = None, body = None, stream = False ):
    req = request( method, url = url, headers = self.token,
        params = params, json = body, stream = stream
    )
    return req if stream else req.json()


class Container( Bytez ):
  def __init__(self, bytez, title):
    super().__init__( user = bytez.user, creds = bytez.creds, token = bytez.token)
    self.type = 'container'
    self.title = title
    self.endpoint = f'{self.endpoint}/{title}'
    self.settings = next(iter(self.request( url = self.endpoint ).values()))

  def edit(self, data):
    return self.request( method = 'patch', url = self.endpoint, body = data )
  def get(self): return self.settings;
  def rows(self): return Rows(self)

class Rows( Container ):
  def __init__(self, bytez ):
    super().__init__(bytez, bytez.title)
    self.type = 'rows'
    self.endpoint = f'{self.endpoint}/rows'
    self.folder = {
      'container': self.title,
      'synced': f'{self.title}/synced',
      'files': f'{self.title}/files'
    }
    if not exists(self.folder['container']): mkdir(self.folder['container'])
    if not exists(self.folder['synced']): mkdir(self.folder['synced'])
    if not exists(self.folder['files']): mkdir(self.folder['files'])

    self.fields = self.settings['schema'].keys() if 'schema' in self.settings else None

    if self.fields is not None and not exists(f'{self.title}/table.csv'):
      with open(f'{self.title}/table.csv','a') as tableCSVFile:
        DictWriter( tableCSVFile, fieldnames = self.fields ).writeheader()

    if not exists(f'{self.title}/labels.csv'):
      with open(f'{self.title}/labels.csv','a') as labelsCSV:
        DictWriter( labelsCSV, fieldnames = ['id','labels'] ).writeheader()


  def get( self, limit = 10000, cursor = None, sync = False ):
    params = { 'limit': limit }
    if cursor: params['cursor'] = cursor

    json = self.request( url = self.endpoint, params = params )

    if 'cursor' in json:
      cursor = json['cursor']
      del json['cursor']
    else:
      cursor = None

    rows = {}

    for rowID, row in json.items():
      rows[ rowID[rowID.rfind('/') + 1:] ] = self.format(row)

    if sync:
      threads = [Thread(target=self.save_to_drive, args=(rowID,row,)) for rowID, row in rows.items()]
      for thread in threads: thread.start()
      for thread in threads: thread.join()

    return rows, cursor
  def edit( self, rowDict ):
    for rowID, row in rowDict.items():
      return self.request( method = 'patch', url = f'{self.endpoint}/{rowID}', body = row )

  # clean the row format
  def format(self, row):
#     if 'row' in row:
#       row['vector'] = row['row']
#       del row['row']

    return row
  def sync(self, cursor = '', limit = None):
    while cursor is not None:
      rows, cursor = self.get( cursor = cursor, sync = True, limit = limit )
  def convertToDataFrame(self):
    folder_container = self.folder['container']
    return pandas.read_csv(f'{folder_container}/table.csv')

  def save_to_drive(self, rowID, row):
    folder_container = self.folder['container']
    folder_synced = self.folder['synced']
    folder_files = self.folder['files']
    # lets make the container as a folder

    if not exists(f'{folder_synced}/{rowID}'):
      open( f'{folder_synced}/{rowID}', 'a' ).close()

      if 'row' in row:
        with open(f'{folder_container}/table.csv','a') as tableCSVFile:
          DictWriter( tableCSVFile, fieldnames = self.fields ).writerow( row['row'] )

      if 'meta' in row and 'labels' in row['meta']:
        with open(f'{folder_container}/labels.csv','a') as labelsCSV:
          labels = ','.join(row['meta']['labels'])
          labelsCSV.write(f'{rowID},{labels}\n')

      if 'file' in row:
        response = self.request( url = row['file']['url'], stream = True )

        if 'name' in row['file']:
          file_name = row['file']['name']
          extension = file_name[ file_name.rfind('.') : ]
        else:
          extension = ''

        with open(f'{folder_files}/{rowID}{extension}', 'wb') as file:
           for chunk in response: file.write(chunk)

  # there is at least 1 GB of space left
  def enoughSpace( units = 'GB' ):
    total, used, free = disk_usage( argv[0] )
    return ( free  / float(1<<(20 if units == 'MB' else 30) ) ) > 1.0
import urllib.request
import urllib.parse
import json
import pandas as pd
import requests
import io
import tqdm
from pathlib import Path
import os
import shutil
from hievpy.utils import *


# ----------------------------------------------------------------------------------------------------------------------
# Generic functions
# ----------------------------------------------------------------------------------------------------------------------

def search(api_token, base_url, search_params):
    """ Returns a list of HIEv records matching a set of input search parameters.

    Input
    -----
    Required
    - api_token: HIEv API token/key
    - base_url: Base URL of the HIEv/Diver instance, e.g. 'https://hiev.uws.edu.au'
    - search_params: Object containing metadata key-value pairs for searching

    Returns
    -------
    List of matching hiev search results (with file download url included)

    """

    request_url = f"{base_url}data_files/api_search"
    request_data = search_params

    # Add Auth/API token to request_data
    request_data['auth_token'] = api_token

    # -- Set up the http request and handle the returned response
    data = urllib.parse.urlencode(request_data, True)
    data = data.encode('ascii')
    req = urllib.request.Request(request_url, data)
    with urllib.request.urlopen(req) as response:
        the_page = response.read()

    encoding = response.info().get_content_charset('utf-8')
    records = json.loads(the_page.decode(encoding))

    return records


def search_download(api_token, base_url, search_params, path=None):
    """ Performs a hievpy search and automatically downloads the matching files.

    Input
    -----
    Required
    - api_token: HIEv API token/key
    - base_url: Base URL of the HIEv/Diver instance, e.g. 'https://hiev.uws.edu.au'
    - search_params: Object containing metadata key-value pairs for searching

    Optional
    - path: Full path of download directory (if path not provided, file will be downloaded to current directory)

    """

    records = search(api_token, base_url, search_params)

    # Download all files returned by the search to the specified folder path (if given)
    for record in tqdm.tqdm(records):
        download_url = f"{record['url']}?auth_token={api_token}"

        if path:
            download_path = Path(path) / record['filename']
            urllib.request.urlretrieve(download_url, download_path)
        else:
            urllib.request.urlretrieve(download_url, record['filename'])


def upload(api_token, base_url, upload_file, metadata):
    """ Uploads a file to HIEv with associated metadata

    Input
    -----
    Required
    - api_token: HIEv API token/key
    - base_url: Base URL of the HIEv/Diver instance, e.g. 'https://hiev.uws.edu.au'
    - upload_file: Full path to the file to be uploaded
    - metadata: Object containing metadata key-value pairs

    """

    upload_url = f"{base_url}data_files/api_create?auth_token={api_token}"
    files = {'file': open(upload_file, 'rb')}
    response = requests.post(upload_url, files=files, data=metadata)

    # Print out the outcome of the upload
    if response.status_code == 200:
        print('File successfully uploaded to HIEv')
    else:
        print('ERROR - There was a problem uploading the file to HIEv')


def update_metadata(api_token, base_url, records, updates):
    """ Updates metadata on a list of records returned by hievpy search

    Input
    -----
    Required
    - api_token: HIEv API token/key
    - base_url: Base URL of the HIEv/Diver instance, e.g. 'https://hiev.uws.edu.au'
    - records: A list of records as returned by the hievpy search function
    - updates: Object containing updated metadata key-value pairs

    """

    update_url = f"{base_url}data_files/api_update?auth_token={api_token}"

    counter = 0
    for record in tqdm.tqdm(records):
        # copy in the original ID of the search record into the file_id field of the updates
        updates['file_id'] = record['file_id']

        response = requests.post(update_url, data=updates)

        # Tally the number of successful updates
        if response.status_code == 200:
            counter += 1

    print(f"{counter} records of {len(records)} successfully updated")


# ---------------------------------------------------------------------------------------------------------------------
# TOA5 functions
# ----------------------------------------------------------------------------------------------------------------------


def toa5_summary(api_token, record):
    """ Returns toa5 summary information (variable names, units and measurement types) for a given
    individual search-returned record.

    Input
    -----
    Required
    - api_token: HIEv API token/key
    - record: individual record object from the results of the hievpy search function

    Returns
    -------
    TOA5 summary information printed to the console
    """

    if is_toa5(record):
        download_url = f"{record['url']}?auth_token={api_token}"
        req = urllib.request.urlopen(download_url)
        data = req.read()
        df = pd.read_csv(io.StringIO(data.decode('utf-8')),
                         skiprows=1, header=None)
        for column in df:
            print("  ".join(str(x) for x in df[column][0:3].values))
    else:
        print('Error: This is not a TOA5 record')


def search_load_toa5df(api_token, base_url, search_params, biggish_data=False,
                       keep_files=False, dst_folder='./raw_data'):
    """ Performs a hievpy search and loads results into a pandas dataframe given the file records

    Input
    -----
    Required
    - api_token: HIEv API token/key
    - base_url: Base URL of the HIEv/Diver instance, e.g. 'https://hiev.uws.edu.au/'
    - search_params: Object containing metadata key-value pairs for searching
    Optional:
    - biggish_data: boolean
        If True files will be downloaded and datatypes optimized for memory
        usage. Handy for large time series and/or using shitty computers.
    - keep_files: boolean
        If True will keep files after importing into dataframe.
    - dst_folder: string
        Path to folder files will be downloaded to.


    Returns
    -------
    Sorted pandas dataframe of TOA5 data with index equal to TIMESTAMP and TOA5 variable names as column headers

    * Notice
    The top row of the original TOA5 file (logger info etc) and the units and measurement type rows are discarded
    during dataframe creation. This information can alternatively be found via the toa5_summary function.

    """
    # search records
    records = search(api_token, base_url, search_params)

    # use 'biggish data' mode
    if biggish_data:
        # set and create download folder if it does not exist
        dst_folder = Path(dst_folder)
        if not dst_folder.is_dir():
            os.makedirs(dst_folder)

        # display number of files beeing downloaded
        print(f'Downloading {len(records)} files:')

        # build download url for each file
        for record in tqdm.tqdm(records):
            download_url = f"{record['url']}?auth_token={api_token}"

            # check if file exists, if not downloads
            file_path = dst_folder / record['filename']
            if not file_path.is_file():
                urllib.request.urlretrieve(download_url, file_path)

        # create empty dataframe to store final data
        df_all = pd.DataFrame()

        # loop through all downloaded files
        for i in list(dst_folder.glob('*.dat')):

            # read data into dataframe discarding undesired header columns
            df = pd.read_csv(i, skiprows=[0, 2, 3], na_values='NAN')

            # generate datetimeindex
            df = df.set_index('TIMESTAMP')
            df.index = pd.to_datetime(df.index)

            # optimize memory usage
            # first get names of float, integer and object columns
            float_cols = df.select_dtypes(include=['float64']).columns
            integer_cols = df.select_dtypes(include=['int64']).columns
            object_cols = df.select_dtypes(include=['object']).columns
            # the assign dtype that uses least memory for each column
            df[integer_cols] = df[integer_cols].apply(
                pd.to_numeric, downcast='integer')
            df[float_cols] = df[float_cols].apply(
                pd.to_numeric, downcast='float')
            # converting objects to category is only more memory efficient if
            # less tha 50% of values are unique
            for col in object_cols:
                num_unique_values = len(df[col].unique())
                num_total_values = len(df[col])
                if num_unique_values / num_total_values < 0.5:
                    df[col] = df[col].astype('category')

            # append data
            df_all = pd.concat([df_all, df], sort=False)

        # delete dst_folder if wanted
        if not keep_files:
            shutil.rmtree(dst_folder)

    else:
        # print number of records found
        print(f'Loading {len(records)} files:')

        # create empty dataframe to save data in
        df_all = pd.DataFrame()

        # loop through all records and generate progressbar
        for record in tqdm.tqdm(records):
            # build download url for each file
            download_url = f"{record['url']}?auth_token={api_token}"
            # get data
            req = urllib.request.urlopen(download_url)
            data = req.read()

            # read data into dataframe discarding undesired header columns
            df = pd.read_csv(io.StringIO(data.decode('utf-8')),
                             skiprows=[0, 2, 3], na_values='NAN')
            # generate datetimeindex
            df = df.set_index('TIMESTAMP')
            df.index = pd.to_datetime(df.index)

            # infer data types of all other columns
            df = df.infer_objects()

            # append data
            df_all = pd.concat([df_all, df], sort=False)


    # if from_date provided sort and trim data
    if 'from_date' in search_params:
        df_all = df_all[search_params['from_date']:].sort_index()
    # if to_date provided sort and trim data
    if 'to_date' in search_params:
        df_all = df_all[:search_params['to_date']].sort_index()

    return df_all.sort_index()

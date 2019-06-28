import os
from threading import Thread
from tabulate import tabulate
from queue import Queue
from .openbis_object import OpenBisObject 
from .definitions import openbis_definitions
from .utils import VERBOSE
import requests
import json
from pandas import DataFrame
#from urllib.parse import urlparse, urljoin, quote
import urllib.parse

# needed for Data upload
PYBIS_PLUGIN = "dataset-uploader-api"
dataset_definitions = openbis_definitions('DataSet')


class DataSet(OpenBisObject):
    """ DataSet are openBIS objects that contain the actual files.
    """

    def __init__(self, openbis_obj, type, data=None, files=None, folder=None, kind=None, props=None, **kwargs):

        if kwargs is None:
            kwargs = {}
        else:
            for key in kwargs:
                if key not in dataset_definitions['attrs_new']:
                    raise ValueError("{} is not a valid attribute for a DataSet".format(key))

        if kind == 'PHYSICAL_DATA':
            if files is None:
                raise ValueError('please provide at least one file')

            if isinstance(files, str):
                files = [files]

            for file in files:
                if not os.path.exists(file):
                    raise ValueError('File {} does not exist'.format(file))


            self.__dict__['files'] = files

        # initialize the attributes
        super(DataSet, self).__init__(openbis_obj, type, data, props, **kwargs)

        self.__dict__['files_in_wsp'] = []

        # existing DataSet
        if data is not None:
            if data['physicalData'] is None:
                self.__dict__['shareId'] = None
                self.__dict__['location'] = None
            else:
                self.__dict__['shareId'] = data['physicalData']['shareId']
                self.__dict__['location'] = data['physicalData']['location']
        

        if kind is not None:
            kind = kind.upper()
            allowed_kinds = ['PHYSICAL_DATA', 'CONTAINER', 'LINK']
            if kind not in allowed_kinds:
                raise ValueError(
                    "only these values are allowed for kind: {}".format(allowed_kinds)
                )
            self.a.__dict__['_kind'] = kind

        self.__dict__['folder'] = folder

        if getattr(self, 'parents') is None:
            self.a.__dict__['_parents'] = []
        else:
            if not self.is_new:
                self.a.__dict__['_parents_orig'] = self.a.__dict__['_parents']

        if getattr(self, 'children') is None:
            self.a.__dict__['_children'] = []
        else:
            if not self.is_new:
                self.a.__dict__['_children_orig'] = self.a.__dict__['_children']

        if getattr(self, 'container') is None:
            self.a.__dict__['_container'] = []
        else:
            if not self.is_new:
                self.a.__dict__['_container_orig'] = self.a.__dict__['_container']

        if getattr(self, 'component') is None:
            self.a.__dict__['_component'] = []
        else:
            if not self.is_new:
                self.a.__dict__['_component_orig'] = self.a.__dict__['_component']


    def __str__(self):
        return self.data['code']

    def __dir__(self):
        return [
            'permId',
            'kind',
            'props', 
            'get_parents()', 'get_children()', 'get_components()', 'get_contained()', 'get_containers()',
            'add_parents()', 'add_children()', 'add_components()', 'add_contained()', 'add_containers()', 
            'del_parents()', 'del_children()', 'del_components()', 'del_contained()', 'del_containers()',
            'set_parents()', 'set_children()', 'set_components()', 'set_contained()', 'set_containers()',
            'sample', 
            'experiment', 
            'collection', 
            'dataStore',
            'physicalData',
            'linkedData',
            'tags', 'set_tags()', 'add_tags()', 'del_tags()',
            'add_attachment()', 'get_attachments()', 'download_attachments()',
            "get_files(start_folder='/')", 'file_list',
            'download(files=None, destination=None, wait_until_finished=True)', 
            'status', 'size', 'archive()', 'unarchive()' 
        ]

    def __setattr__(self, name, value):
        if name in ['folder']:
            self.__dict__[name] = value
        else:
            super(DataSet, self).__setattr__(name, value)

    @property
    def props(self):
        return self.__dict__['p']

    @property
    def type(self):
        return self.__dict__['type']

    @type.setter
    def type(self, type_name):
        dataset_type = self.openbis.get_dataset_type(type_name.upper())
        self.p.__dict__['_type'] = dataset_type
        self.a.__dict__['_type'] = dataset_type

    @property
    def physicalData(self):
        if 'physicalData' in self.data:
            return PhysicalData(data=self.data['physicalData'])

    @property
    def linkedData(self):
        if 'linkedData' in self.data:
            return LinkedData(self.data['linkedData'])

    @property
    def status(self):
        ds = self.openbis.get_dataset(self.permId)
        self.data['physicalData'] = ds.data['physicalData']
        try:
            return self.data['physicalData']['status']
        except Exception:
            return None

    def archive(self, remove_from_data_store=True):
        fetchopts = {
            "removeFromDataStore": remove_from_data_store,
            "@type": "as.dto.dataset.archive.DataSetArchiveOptions"
        }
        self.archive_unarchive('archiveDataSets', fetchopts)
        if VERBOSE: print("DataSet {} archived".format(self.permId))

    def unarchive(self):
        fetchopts = {
            "@type": "as.dto.dataset.unarchive.DataSetUnarchiveOptions"
        }
        self.archive_unarchive('unarchiveDataSets', fetchopts)
        if VERBOSE: print("DataSet {} unarchived".format(self.permId))

    def archive_unarchive(self, method, fetchopts):
        payload = {}

        request = {
            "method": method,
            "params": [
                self.openbis.token,
                [{
                    "permId": self.permId,
                    "@type": "as.dto.dataset.id.DataSetPermId"
                }],
                dict(fetchopts)
            ],
        }
        resp = self.openbis._post_request(self._openbis.as_v3, request)
        return

    def set_properties(self, properties):
        """expects a dictionary of property names and their values.
        Does not save the dataset.
        """
        for prop in properties.keys():
            setattr(self.p, prop, properties[prop])

    set_props = set_properties

    def download(self, files=None, destination=None, wait_until_finished=True, workers=10,
        linked_dataset_fileservice_url=None, content_copy_index=0):
        """ download the actual files and put them by default in the following folder:
        __current_dir__/destination/dataset_permId/
        If no files are specified, all files of a given dataset are downloaded.
        If no destination is specified, the hostname is chosen instead.
        Files are usually downloaded in parallel, using 10 workers by default. If you want to wait until
        all the files are downloaded, set the wait_until_finished option to True.
        """

        if files == None:
            files = self.file_list
        elif isinstance(files, str):
            files = [files]

        if destination is None:
            destination = self.openbis.hostname
        
        kind = None;
        if 'kind' in self.data: # openBIS 18.6.x DTO
            kind = self.data['kind']
        elif ('type' in self.data) and ('kind' in self.data['type']): # openBIS 16.5.x DTO
            kind =self.data['type']['kind']
        
        if kind == 'PHYSICAL':
            return self._download_physical(files, destination, wait_until_finished, workers)
        elif kind == 'LINK':
            if linked_dataset_fileservice_url is None:
                raise ValueError("Can't download a LINK data set without the linked_dataset_fileservice_url parameters.")
            return self._download_link(files, destination, wait_until_finished, workers, linked_dataset_fileservice_url, content_copy_index)
        else:
            raise ValueError("Can't download data set of kind {}.".format(kind))


    def _download_physical(self, files, destination, wait_until_finished, workers):
        """ Download for data sets of kind PHYSICAL.
        """

        base_url = self.data['dataStore']['downloadUrl'] + '/datastore_server/' + self.permId + '/'

        queue = DataSetDownloadQueue(workers=workers)

        # get file list and start download
        for filename in files:
            file_info = self.get_file_list(start_folder=filename)
            file_size = file_info[0]['fileSize']
            download_url = base_url + filename + '?sessionID=' + self.openbis.token
            filename_dest = os.path.join(destination, self.permId, filename)
            queue.put([download_url, filename, filename_dest, file_size, self.openbis.verify_certificates, 'wb'])

        # wait until all files have downloaded
        if wait_until_finished:
            queue.join()

        if VERBOSE: print("Files downloaded to: %s" % os.path.join(destination, self.permId))
        return destination


    def _download_link(self, files, destination, wait_until_finished, workers, linked_dataset_fileservice_url, content_copy_index):
        """ Download for data sets of kind LINK.
        Requires the microservice server to be running at the given linked_dataset_fileservice_url.
        """

        queue = DataSetDownloadQueue(workers=workers, collect_files_with_wrong_length=True)

        if content_copy_index >= len(self.data["linkedData"]["contentCopies"]):
            raise ValueError("Content Copy index out of range.")
        content_copy = self.data["linkedData"]["contentCopies"][content_copy_index]

        for filename in files:
            file_info = self.get_file_list(start_folder=filename)
            file_size = file_info[0]['fileSize']

            download_url = linked_dataset_fileservice_url
            download_url += "?sessionToken=" + self.openbis.token
            download_url += "&datasetPermId=" + self.data["permId"]["permId"]
            download_url += "&externalDMSCode=" + content_copy["externalDms"]["code"]
            download_url += "&contentCopyPath=" + content_copy["path"].replace("/", "%2F")
            download_url += "&datasetPathToFile=" + urllib.parse.quote(filename)

            filename_dest = os.path.join(destination, self.permId, filename)

            # continue download if file is not complete - do nothing if it is
            write_mode = 'wb'
            if os.path.exists(filename_dest):
                actual_size = os.path.getsize(filename_dest)
                if actual_size == int(file_size):
                    continue
                elif actual_size < int(file_size):
                    write_mode = 'ab'
                    download_url += "&offset=" + str(actual_size)

            queue.put([download_url, filename, filename_dest, file_size, self.openbis.verify_certificates, write_mode])

        if wait_until_finished:
            queue.join()

        if VERBOSE: print("Files downloaded to: %s" % os.path.join(destination, self.permId))
        return destination, queue.files_with_wrong_length


    @property
    def folder(self):
        return self.__dict__['folder']

    @property
    def file_list(self):
        """returns the list of files including their directories as an array of strings. Just folders are not
        listed.
        """

        if self.is_new:
            return self.files
        else:
            files = []
            for file in self.get_file_list(recursive=True):
                if file['isDirectory']:
                    pass
                else:
                    files.append(file['pathInDataSet'])
            return files

    def get_files(self, start_folder='/'):
        """Returns a DataFrame of all files in this dataset
        """

        def createRelativePath(pathInDataSet):
            if self.shareId is None:
                return ''
            else:
                return os.path.join(self.shareId, self.location, pathInDataSet)

        def signed_to_unsigned(sig_int):
            """openBIS delivers crc32 checksums as signed integers.
            If the number is negative, we just have to add 2**32
            We display the hex number to match with the classic UI
            """
            if sig_int < 0:
                sig_int += 2 ** 32
            return "%x" % (sig_int & 0xFFFFFFFF)

        files = self.get_file_list(start_folder=start_folder)
        df = DataFrame(files)
        df['relativePath'] = df['pathInDataSet'].map(createRelativePath)
        df['crc32Checksum'] = df['crc32Checksum'].fillna(0.0).astype(int).map(signed_to_unsigned)
        return df[['isDirectory', 'pathInDataSet', 'fileSize', 'crc32Checksum']]

    def get_file_list(self, recursive=True, start_folder="/"):
        """Lists all files of a given dataset. You can specifiy a start_folder other than "/".
        By default, all directories and their containing files are listed recursively. You can
        turn off this option by setting recursive=False.
        """
        request = {
            "method": "listFilesForDataSet",
            "params": [
                self.openbis.token,
                self.permId,
                start_folder,
                recursive,
            ],
            "id": "1"
        }

        resp = requests.post(
            self.data["dataStore"]["downloadUrl"] + '/datastore_server/rmi-dss-api-v1.json',
            json.dumps(request),
            verify=self.openbis.verify_certificates
        )

        if resp.ok:
            data = resp.json()
            if 'error' in data:
                raise ValueError('Error from openBIS: ' + data['error']['message'])
            elif 'result' in data:
                return data['result']
            else:
                raise ValueError('request to openBIS did not return either result nor error')
        else:
            raise ValueError('internal error while performing post request')


    def _generate_plugin_request(self, dss, permId=None):
        """generates a request to activate the dataset-uploader ingestion plugin to
        register our files as a new dataset
        """

        sample_identifier = None
        if self.sample is not None:
            sample_identifier = self.sample.identifier

        experiment_identifier = None
        if self.experiment is not None:
            experiment_identifier = self.experiment.identifier

        parentIds = self.parents
        if parentIds is None:
            parentIds = []

        dataset_type = self.type.code
        properties = self.props.all_nonempty()

        request = {
            "method": "createReportFromAggregationService",
            "params": [
                self.openbis.token,
                dss,
                PYBIS_PLUGIN,
                {
                    "permId" : permId,
                    "method" : "insertDataSet",
                    "sampleIdentifier" : sample_identifier,
                    "experimentIdentifier" : experiment_identifier,
                    "dataSetType" : dataset_type,
                    "folderName" : self.folder,
                    "fileNames" : self.files_in_wsp,
                    "isZipDirectoryUpload" : False,
                    "properties" : properties,
                    "parentIdentifiers": parentIds
                }
            ],
        }
        return request

    def delete(self, reason):
        self.openbis.delete_entity(entity='DataSet',id=self.permId, reason=reason)
        if VERBOSE: print("DataSet {} successfully deleted.".format(self.permId))


    def save(self, permId=None):
        for prop_name, prop in self.props._property_names.items():
            if prop['mandatory']:
                if getattr(self.props, prop_name) is None or getattr(self.props, prop_name) == "":
                    raise ValueError("Property '{}' is mandatory and must not be None".format(prop_name))

        if self.is_new:
            datastores = self.openbis.get_datastores()
 
            if self.sample is None and self.experiment is None:
                raise ValueError('A DataSet must be either connected to a Sample or an Experiment')

            if self.kind == 'PHYSICAL_DATA':
                if self.files is None or len(self.files) == 0:
                    raise ValueError(
                        'Cannot register a dataset without a file. Please provide at least one file'
                    )
                
                # for uploading phyiscal data, we first upload it to the session workspace
                self.upload_files(
                    datastore_url= datastores['downloadUrl'][0],
                    files=self.files,
                    folder='',
                    wait_until_finished=True
                )

                # activate the ingestion plugin, as soon as the data is uploaded
                # this will actually register the dataset in the datastore and the AS
                request = self._generate_plugin_request(dss=datastores['code'][0], permId=permId)
                resp = self.openbis._post_request(self.openbis.reg_v1, request)
                if resp['rows'][0][0]['value'] == 'OK':
                    permId = resp['rows'][0][2]['value']
                    if permId is None or permId == '': 
                        self.__dict__['is_new'] = False
                        if VERBOSE: print("DataSet successfully created. Because you connected to an openBIS version older than 16.05.04, you cannot update the object.")
                    else:
                        new_dataset_data = self.openbis.get_dataset(permId, only_data=True)
                        self._set_data(new_dataset_data)
                        if VERBOSE: print("DataSet successfully created.")
                        return self
                else:
                    raise ValueError('Error while creating the DataSet: ' + resp['rows'][0][1]['value'])
            # CONTAINER 
            else:
                if self.files is not None and len(self.files) > 0:
                    raise ValueError(
                        'DataSets of kind CONTAINER or LINK cannot contain data'
                    )

                request = self._new_attrs() 

                # if no code for the container was provided, let openBIS
                # generate the code automatically
                if self.code is None or self.code == "":
                    request['params'][1][0]['autoGeneratedCode'] = True
                else:
                    request['params'][1][0]['autoGeneratedCode'] = False

                props = self.p._all_props()
                DSpermId = datastores['code'][0]
                request["params"][1][0]["properties"] = props
                request["params"][1][0]["dataStoreId"] = {
                    "permId": DSpermId,
                    "@type": "as.dto.datastore.id.DataStorePermId"
                }
                resp = self.openbis._post_request(self.openbis.as_v3, request)

                if VERBOSE: print("DataSet successfully created.")
                new_dataset_data = self.openbis.get_dataset(resp[0]['permId'], only_data=True)
                self._set_data(new_dataset_data)
                return self

            
        # updating the DataSEt
        else:
            request = self._up_attrs()
            props = self.p._all_props()
            request["params"][1][0]["properties"] = props

            self.openbis._post_request(self.openbis.as_v3, request)
            if VERBOSE: print("DataSet successfully updated.")


    def upload_files(self, datastore_url=None, files=None, folder=None, wait_until_finished=False):

        if datastore_url is None:
            datastore_url = self.openbis._get_dss_url()

        if files is None:
            raise ValueError("Please provide a filename.")

        if folder is None:
            # create a unique foldername
            folder = time.strftime('%Y-%m-%d_%H-%M-%S')

        if isinstance(files, str):
            files = [files]

        # define a queue to handle the upload threads
        queue = DataSetUploadQueue()

        real_files = []
        for filename in files:
            if os.path.isdir(filename):
                real_files.extend(
                    [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(filename)) for f in fn])
            else:
                real_files.append(os.path.join(filename))

        # compose the upload-URL and put URL and filename in the upload queue 
        for filename in real_files:
            file_in_wsp = os.path.join(folder, os.path.basename(filename))
            url_filename = os.path.join(folder, urllib.parse.quote(os.path.basename(filename)))
            self.files_in_wsp.append(file_in_wsp)

            upload_url = (
                datastore_url + '/datastore_server/session_workspace_file_upload'
                + '?filename=' + url_filename
                + '&id=1'
                + '&startByte=0&endByte=0'
                + '&sessionID=' + self.openbis.token
            )
            queue.put([upload_url, filename, self.openbis.verify_certificates])

        # wait until all files have uploaded
        if wait_until_finished:
            queue.join()

        # return files with full path in session workspace
        return self.files_in_wsp


class DataSetUploadQueue():
    def __init__(self, workers=20):
        # maximum files to be uploaded at once
        self.upload_queue = Queue()

        # define number of threads and start them
        for t in range(workers):
            t = Thread(target=self.upload_file)
            t.daemon = True
            t.start()

    def put(self, things):
        """ expects a list [url, filename] which is put into the upload queue
        """
        self.upload_queue.put(things)

    def join(self):
        """ needs to be called if you want to wait for all uploads to be finished
        """
        self.upload_queue.join()

    def upload_file(self):
        while True:
            # get the next item in the queue
            upload_url, filename, verify_certificates = self.upload_queue.get()

            filesize = os.path.getsize(filename)

            # upload the file to our DSS session workspace
            with open(filename, 'rb') as f:
                resp = requests.post(upload_url, data=f, verify=verify_certificates)
                resp.raise_for_status()
                data = resp.json()
                assert filesize == int(data['size'])

            # Tell the queue that we are done
            self.upload_queue.task_done()


class DataSetDownloadQueue():
    def __init__(self, workers=20, collect_files_with_wrong_length=False):
        self.collect_files_with_wrong_length = collect_files_with_wrong_length
        # maximum files to be downloaded at once
        self.download_queue = Queue()
        self.files_with_wrong_length = []

        # define number of threads
        for t in range(workers):
            t = Thread(target=self.download_file)
            t.daemon = True
            t.start()

    def put(self, things):
        """ expects a list [url, filename] which is put into the download queue
        """
        self.download_queue.put(things)

    def join(self):
        """ needs to be called if you want to wait for all downloads to be finished
        """
        self.download_queue.join()

    def download_file(self):
        while True:
            try:
                url, filename, filename_dest, file_size, verify_certificates, write_mode = self.download_queue.get()
                # create the necessary directory structure if they don't exist yet
                os.makedirs(os.path.dirname(filename_dest), exist_ok=True)

                # request the file in streaming mode
                r = requests.get(url, stream=True, verify=verify_certificates)
                if r.ok == False:
                    raise ValueError("Could not download from {}: HTTP {}. Reason: {}".format(url, r.status_code, r.reason))

                with open(filename_dest, write_mode) as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)

                if os.path.getsize(filename_dest) != int(file_size):
                    if self.collect_files_with_wrong_length:
                        self.files_with_wrong_length.append(filename)
                    else:
                        raise ValueError("File has the wrong length: {}".format(filename_dest))
            finally:
                self.download_queue.task_done()


class PhysicalData():
    def __init__(self, data=None):
        if data is None:
            data = {}
        self.data = data
        self.attrs = ['speedHint', 'complete', 'shareId', 'size',
                      'fileFormatType', 'storageFormat', 'location', 'presentInArchive',
                      'storageConfirmation', 'locatorType', 'status']

    def __dir__(self):
        return self.attrs

    def __getattr__(self, name):
        if name in self.attrs:
            if name in self.data:
                return self.data[name]

    def __getitem__(self, key):
        if key in self.attrs:
            if key in self.data:
                return self.data[key]

    def _repr_html_(self):
        html = """
            <table border="1" class="dataframe">
            <thead>
                <tr style="text-align: right;">
                <th>attribute</th>
                <th>value</th>
                </tr>
            </thead>
            <tbody>
        """

        for attr in self.attrs:
            html += "<tr> <td>{}</td> <td>{}</td> </tr>".format(
                attr, getattr(self, attr, '')
            )

        html += """
            </tbody>
            </table>
        """
        return html

    def __repr__(self):
        headers = ['attribute', 'value']
        lines = []
        for attr in self.attrs:
            lines.append([
                attr,
                getattr(self, attr, '')
            ])
        return tabulate(lines, headers=headers)


class LinkedData():
    def __init__(self, data=None):
        self.data = data if data is not None else []
        self.attrs = ['externalCode', 'contentCopies']

    def __dir__(self):
        return self.attrs

    def __getattr__(self, name):
        if name in self.attrs:
            if name in self.data:
                return self.data[name]
        else:
            return ''


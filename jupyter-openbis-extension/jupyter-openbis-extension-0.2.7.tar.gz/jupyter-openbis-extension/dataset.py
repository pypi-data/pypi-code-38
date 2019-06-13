import os
from urllib.parse import unquote
from notebook.base.handlers import IPythonHandler
from .connection import openbis_connections

class DataSetDownloadHandler(IPythonHandler):
    """Handle the requests for /openbis/dataset/connection/permId"""


    def download_data(self, conn, permId, downloadPath=None):
        if not conn.is_session_active():
            try:
                conn.login()
            except Exception as exc:
                self.set_status(500)
                self.write({
                    "reason" : 'connection to {} could not be established: {}'.format(conn.name, exc)
                })
                return

        try:
            dataset = conn.openbis.get_dataset(permId)
        except Exception as exc:
            self.set_status(404)
            self.write({
                "reason" : 'No such dataSet found: {}'.format(permId)
            })
            return

        # dataset was found, download the data to the disk
        try:
            destination = dataset.download(destination=downloadPath)
        except Exception as exc:
            self.set_status(500)
            self.write({
                "reason": 'Data for DataSet {} could not be downloaded: {}'.format(permId, exc)
            })
            return

        # return success message
        path = os.path.join(downloadPath, dataset.permId)
        self.write({
            'url'       : conn.url,
            'permId'    : dataset.permId,
            'path'      : path,
            'dataStore' : dataset.dataStore,
            'location'  : dataset.physicalData.location,
            'size'      : dataset.physicalData.size,
            'statusText': 'Data for DataSet {} was successfully downloaded to: {}.'.format(dataset.permId, path)
        })

    def get(self, **params):
        """Handle a request to /openbis/dataset/connection_name/permId
        download the data and return a message
        """

        try:
            conn = openbis_connections[params['connection_name']]
        except KeyError:
            self.set_status(404)
            self.write({
                "reason":'connection {} was not found'.format(params['connection_name'])
            })
            return

        results = self.download_data(conn=conn, permId=params['permId'], downloadPath=params['downloadPath'])


class DataSetTypesHandler(IPythonHandler):
    def get(self, **params):
        """Handle a request to /openbis/datasetTypes/connection_name
        """

        try:
            conn = openbis_connections[params['connection_name']]
        except KeyError:
            self.set_status(404)
            self.write({
                "reason":'connection {} was not found'.format(params['connection_name'])
            })
            return

        try:
            dataset_types = conn.openbis.get_dataset_types()
            dts = dataset_types.df.to_dict(orient='records')

            # get property assignments for every dataset-type
            # and add it to the dataset collection
            for dt in dts:
                dataset_type = conn.openbis.get_dataset_type(dt['code'])
                pa = dataset_type.get_propertyAssignments(including_vocabulary=True)
                pa_dicts = pa.to_dict(orient='records')
                for pa_dict in pa_dicts:
                    if pa_dict['dataType'] == 'CONTROLLEDVOCABULARY':
                        terms = conn.openbis.get_terms(pa_dict['vocabulary']['code'])
                        pa_dict['terms'] = terms.df[['code','label','description','official','ordinal']].to_dict(orient='records')

                dt['propertyAssignments'] = pa_dicts

            self.write({
                "dataSetTypes": dts
            })
            return

        except Exception as e:
            print(e)
            self.set_status(500)
            self.write({
                "reason":'Could not fetch dataset-types: {}'.format(e)
            })
            return


class DataSetUploadHandler(IPythonHandler):
    """Handle the POST requests for /openbis/dataset/connection_name"""

    def upload_data(self, conn, data):
        if not conn.is_session_active():
            try:
                conn.login()
            except Exception as e:
                print(e)
                self.set_status(500)
                self.write({
                    "reason": 'connection to {} could not be established: {}'.format(conn.name, e)
                })
                return

        errors = []

        sample = None
        experiment = None

        if (data.get('entityIdentifier')):
            sample = None
            experiment = None
            try:
                sample = conn.openbis.get_sample(data.get('entityIdentifier'))
            except Exception as e:
                pass
            if sample is None:
                try:
                    experiment = conn.openbis.get_experiment(data.get('entityIdentifier'))
                except Exception as e:
                    pass

            if sample is None and experiment is None:
                errors.append(
                    {"entityIdentifier" : 'No such sample or experiment: {}'.format(data.get('entityIdentifier')) }
                )
        else:
            errors.append(
                {"entityIdentifier": "please provide a sample or experiment identifier"}
            )

        parents = []
        if data.get('parents'):
            parents = data.get('parents')
            for parent in parents:
                try:
                    conn.openbis.get_dataset(parent)
                except Exception as e:
                    errors.append({
                        "parent": "Parent DataSet not found: {}".format(parent)
                    })

        filenames = []
        for filename in data.get('files'):
            filename = unquote(filename)
            if os.path.isfile(filename):
                filenames.append(filename)
            else:
                errors.append({
                    "file": "File not found: {}".format(filename)
                })

        try:
            dataset = conn.openbis.new_dataset(
                type   = data.get('type'),
                sample = sample,
                parents = parents,
                experiment = experiment,
                files  = filenames,
            )
        except Exception as e:
            print(e)
            errors.append({
                "create": 'Error while creating the dataset: {}'.format(e)
            })

        # try to set the properties
        if data.get('props'):
            props = data.get('props')
            for prop, value in props.items():
                try:
                    setattr(dataset.props, prop.lower(), value)
                except Exception as e:
                    errors.append({
                        "prop."+prop : str(e)
                    })

        # check if any mandatory property is missing
        for prop_name, prop in dataset.props._property_names.items():
            if prop['mandatory']:
                if getattr(dataset.props, prop_name) is None or getattr(dataset.props, prop_name) == "":
                    errors.append({
                        "prop."+prop_name : "is mandatory"
                    })

        # write errors back if already occured
        if errors:
            self.set_status(500)
            self.write({ "errors": errors })
            return

        try:
            dataset.save()
        except Exception as e:
            errors.append({
                "save": 'Error while saving the dataset: {}'.format(e)
            })

        # write errors back if they occured
        if errors:
            self.set_status(500)
            self.write({ "errors": errors })
        else:
            # ...or return a success message
            self.write({
                'status': 200,
                'statusText': 'Jupyter Notebook was successfully uploaded to: {} with permId: {}'.format(conn.name, dataset.permId)
            })
        print('Jupyter Notebook was successfully uploaded to: {} with permId: {}'.format(conn.name, dataset.permId))

    def post(self, **params):
        """Handle a request to /openbis/dataset/connection_name/permId
        download the data and return a message
        """

        try:
            conn = openbis_connections[params['connection_name']]
        except KeyError:
            self.write({
                "reason": 'connection {} was not found'.format(params['connection_name'])
            })
            return

        data = self.get_json_body()
        self.upload_data(conn=conn,data=data)


class FileListHandler(IPythonHandler):

    def get(self, **params):
        """
        Returns the file list of the current working directory

        :param params:
        :return: dictionary of files, key is the fully qualified name,
                 value is the relative name (for display)
        """

        cwd = os.getcwd()
        files = {}
        for (dirpath, dirnames, filenames) in os.walk(cwd):
            if filenames:
                for filename in filenames:
                    # ignore hidden files
                    if filename.startswith('.'):
                        continue
                    # ignore hidden folders
                    if os.path.relpath(dirpath) != '.' \
                            and os.path.relpath(dirpath).startswith('.'):
                        continue
                    fqn = os.path.join(dirpath, filename)
                    files[fqn] = os.path.relpath(fqn, cwd)

        self.set_status(200)
        self.write({
            "files": files
        })


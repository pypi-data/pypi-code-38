################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

from __future__ import print_function
from watson_machine_learning_client.libs.repo.mlrepositoryartifact import MLRepositoryArtifact
from watson_machine_learning_client.libs.repo.mlrepository import MetaProps, MetaNames
import requests
from watson_machine_learning_client.utils import MODEL_DETAILS_TYPE, INSTANCE_DETAILS_TYPE, load_model_from_directory, STR_TYPE, STR_TYPE_NAME, docstring_parameter, meta_props_str_conv, str_type_conv
from watson_machine_learning_client.metanames import ModelMetaNames,LibraryMetaNames
import os
import copy
import json
from watson_machine_learning_client.wml_client_error import WMLClientError
from watson_machine_learning_client.wml_resource import WMLResource
from watson_machine_learning_client.libs.repo.util.compression_util import CompressionUtil
from watson_machine_learning_client.libs.repo.util.unique_id_gen import uid_generate
from watson_machine_learning_client.href_definitions import API_VERSION, SPACES,PIPELINES, LIBRARIES, EXPERIMENTS, RUNTIMES, DEPLOYMENTS


import shutil
import re

_DEFAULT_LIST_LENGTH = 50


class Models(WMLResource):
    """
    Store and manage your models.
    """
    ConfigurationMetaNames = ModelMetaNames()
    LibraryMetaNames = LibraryMetaNames()
    """MetaNames for models creation."""

    def __init__(self, client):
        WMLResource.__init__(self, __name__, client)
        if not client.ICP:
            Models._validate_type(client.service_instance.details, u'instance_details', dict, True)
            Models._validate_type_of_details(client.service_instance.details, INSTANCE_DETAILS_TYPE)
        self._ICP = client.ICP
    def _save_library_archive(self, ml_pipeline):

        id_length = 20
        gen_id = uid_generate(id_length)
        temp_dir_name = '{}'.format("library" + gen_id)
        # if (self.hummingbird_env == 'HUMMINGBIRD') is True:
        #     temp_dir = os.path.join('/home/spark/shared/wml/repo/extract_', temp_dir_name)
        # else:
        temp_dir = os.path.join('.', temp_dir_name)
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        ml_pipeline.write().overwrite().save(temp_dir)
        archive_path = self._compress_artifact(temp_dir)
        shutil.rmtree(temp_dir)
        return archive_path

    def _compress_artifact(self, compress_artifact):
        tar_filename = '{}_content.tar'.format('library')
        gz_filename = '{}.gz'.format(tar_filename)
        CompressionUtil.create_tar(compress_artifact, '.', tar_filename)
        CompressionUtil.compress_file_gzip(tar_filename, gz_filename)
        os.remove(tar_filename)
        return gz_filename
    def _create_pipeline_input(self,lib_href,name,space_uid=None):
        metadata = {
            self._client.pipelines.ConfigurationMetaNames.NAME: name + "_"+uid_generate(8),
            self._client.pipelines.ConfigurationMetaNames.DOCUMENT: {
                "doc_type": "pipeline",
                 "version": "2.0",
                 "primary_pipeline": "dlaas_only",
                 "pipelines": [
                   {
                     "id": "dlaas_only",
                     "runtime_ref": "spark",
                     "nodes": [
                       {
                         "id": "repository",
                         "type": "model_node",
                         "inputs": [
                         ],
                         "outputs": [],
                         "parameters": {
                           "training_lib_href": lib_href + "/content"
                         }
                       }
                     ]
                   }
                 ]
            }
        }
        if space_uid is not None:
            metadata.update({self._client.pipelines.ConfigurationMetaNames.SPACE_UID  : space_uid})
        return metadata
    def _publish_from_object(self, model, meta_props, training_data=None, training_target=None, pipeline=None, feature_names=None, label_column_names=None):
        """
        Store model from object in memory into Watson Machine Learning repository on Cloud
        """
        self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.NAME, STR_TYPE, True)

        try:
            if 'pyspark.ml.pipeline.PipelineModel' in str(type(model)):
                if(pipeline is None or training_data is None):
                    raise WMLClientError(u'pipeline and training_data are expected for spark models.')
                name = meta_props[self.ConfigurationMetaNames.NAME]
                version = "1.0"
                platform = {"name":"python", "versions":["3.5"]}
                library_tar = self._save_library_archive(pipeline)
                lib_metadata = {
                    self.LibraryMetaNames.NAME: name + "_"+uid_generate(8),
                    self.LibraryMetaNames.VERSION: version,
                    self.LibraryMetaNames.PLATFORM: platform,
                    self.LibraryMetaNames.FILEPATH: library_tar
                }
                if self.ConfigurationMetaNames.SPACE_UID in meta_props:
                    lib_metadata.update({self.LibraryMetaNames.SPACE_UID : meta_props[self._client.repository.ModelMetaNames.SPACE_UID]})

                library_artifact = self._client.runtimes.store_library(meta_props = lib_metadata)
                lib_href = self._client.runtimes.get_library_href(library_artifact)
                space_uid =None

                if self.ConfigurationMetaNames.SPACE_UID in meta_props:
                 space_uid = meta_props[self._client.repository.ModelMetaNames.SPACE_UID]

                pipeline_metadata = self._create_pipeline_input(lib_href,name,space_uid=space_uid)
                pipeline_save = self._client.pipelines.store(pipeline_metadata)

                pipeline_href = self._client.pipelines.get_href(pipeline_save)

                meta_props[self._client.repository.ModelMetaNames.PIPELINE_UID] =  {"href": pipeline_href}

                if self.ConfigurationMetaNames.SPACE_UID in meta_props:
                    self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.SPACE_UID, STR_TYPE, False)
                    meta_props[self._client.repository.ModelMetaNames.SPACE_UID] = {"href": API_VERSION + SPACES + "/" + meta_props[self._client.repository.ModelMetaNames.SPACE_UID]}

                if self.ConfigurationMetaNames.RUNTIME_UID in meta_props:
                    self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.RUNTIME_UID, STR_TYPE, False)
                    meta_props[self._client.repository.ModelMetaNames.RUNTIME_UID] = {"href": API_VERSION + RUNTIMES + "/" + meta_props[self._client.repository.ModelMetaNames.RUNTIME_UID]}

                if self.ConfigurationMetaNames.TRAINING_LIB_UID in meta_props:
                    self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.TRAINING_LIB_UID, STR_TYPE, False)
                    meta_props[self._client.repository.ModelMetaNames.TRAINING_LIB_UID] = {"href": API_VERSION + LIBRARIES + "/" + meta_props[self._client.repository.ModelMetaNames.TRAINING_LIB_UID]}

                meta_data = MetaProps(self._client.repository._meta_props_to_repository_v3_style(meta_props))

                model_artifact = MLRepositoryArtifact(model, name=str(meta_props[self.ConfigurationMetaNames.NAME]), meta_props=meta_data, training_data=training_data)
            else:
                if self.ConfigurationMetaNames.SPACE_UID in meta_props:
                    self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.SPACE_UID, STR_TYPE, False)
                    meta_props[self._client.repository.ModelMetaNames.SPACE_UID] = {"href": API_VERSION + SPACES + "/" + meta_props[self._client.repository.ModelMetaNames.SPACE_UID]}

                if self.ConfigurationMetaNames.RUNTIME_UID in meta_props:
                    self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.RUNTIME_UID, STR_TYPE, False)
                    meta_props[self._client.repository.ModelMetaNames.RUNTIME_UID] = {"href": API_VERSION + RUNTIMES + "/" + meta_props[self._client.repository.ModelMetaNames.RUNTIME_UID]}

                if self.ConfigurationMetaNames.TRAINING_LIB_UID in meta_props:
                    self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.TRAINING_LIB_UID, STR_TYPE, False)
                    meta_props[self._client.repository.ModelMetaNames.TRAINING_LIB_UID] = {"href": API_VERSION + LIBRARIES + "/" + meta_props[self._client.repository.ModelMetaNames.TRAINING_LIB_UID]}

                meta_data = MetaProps(self._client.repository._meta_props_to_repository_v3_style(meta_props))
                model_artifact = MLRepositoryArtifact(model, name=str(meta_props[self.ConfigurationMetaNames.NAME]), meta_props=meta_data, training_data=training_data, training_target=training_target, feature_names=feature_names, label_column_names=label_column_names)

            saved_model = self._client.repository._ml_repository_client.models.save(model_artifact)
        except Exception as e:
            raise WMLClientError(u'Publishing model failed.', e)
        else:
            return self.get_details(u'{}'.format(saved_model.uid))

    def _get_subtraining_object(self,trainingobject,subtrainingId):
        subtrainings = trainingobject["entity"]["sub_trainings"]
        for each_training in subtrainings:
            if each_training["metadata"]["guid"] == subtrainingId:
                return each_training
        raise WMLClientError("The subtrainingId " + subtrainingId + " is not found")

    ##TODO not yet supported

    def _publish_from_training(self, model_uid, meta_props, training_data=None, training_target=None,version=False,artifactId=None,subtrainingId=None):
        """
                Store trained model from object storage into Watson Machine Learning repository on IBM Cloud
        """
        model_meta = self.ConfigurationMetaNames._generate_resource_metadata(
            meta_props,
            client=self._client
        )
        self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.NAME, STR_TYPE, True)

        details = self._client.training.get_details(model_uid)
        model_type = ""
        runtime_uid = ""

        ##Check if the training is created from pipeline or experiment

        if "pipeline" in details["entity"]:
            href = details["entity"]["pipeline"]["href"]
            pipeline_id = href.split("/")[3]
            if "model_type" in details["entity"]["pipeline"]:
                model_type = details["entity"]["pipeline"]["model_type"]
                #runtime_uid = model_type + "-py3"
        # if "experiment" in details["entity"]:
        #     if subtrainingId is None:
        #         raise WMLClientError("For a training created via experiment, it is mandatory to specify subtrainingId.")
        #     exp_href = details["entity"]["experiment"]["href"]
        #
        #     exp_id = exp_href.split("/")[3]
        #     exp_details = self._client.experiments.get_details(exp_id)
        #
        #     href = exp_details["entity"]["training_references"][0]["pipeline"]["href"]
        #     if "model_type" in  exp_details["entity"]["training_references"][0]["pipeline"]:
        #         model_type = details["entity"]["pipeline"]["model_type"]
        #         #runtime_uid = model_type + "-py3"

        if "experiment" in details["entity"]:
            subtraining_object = self._get_subtraining_object(details,subtrainingId)
            model_meta.update({"import": subtraining_object["entity"]["results_reference"]})
            pipeline_id =  subtraining_object["entity"]["pipeline"]["href"].split("/")[3]
            if "model_type" in subtraining_object["entity"]["pipeline"]:
                 model_type = subtraining_object["entity"]["pipeline"]["model_type"]
                #runtime_uid = model_type + "-py3"
        else:
            model_meta.update({"import": details["entity"]["results_reference"]})


        definition_details = self._client.pipelines.get_details(pipeline_id)
        runtime_uid = definition_details["entity"]["document"]["runtimes"][0]["name"] + "_" + \
                         definition_details["entity"]["document"]["runtimes"][0]["version"].split("-")[0] + "-py3"
        if model_type == "":
            model_type = definition_details["entity"]["document"]["runtimes"][0]["name"] + "_" + \
                         definition_details["entity"]["document"]["runtimes"][0]["version"].split("-")[0]

        if self.ConfigurationMetaNames.TYPE not in meta_props:
            model_meta.update({"type": model_type})

        if self.ConfigurationMetaNames.RUNTIME_UID not in meta_props:
            model_meta.update({"runtime": {"href": "/v4/runtimes/"+runtime_uid}})

        if not self._ICP:
                creation_response = requests.post(
                       self._wml_credentials['url'] + '/v4/models',
                       headers=self._client._get_headers(),
                       json=model_meta
                )
        else:
                creation_response = requests.post(
                    self._wml_credentials['url'] + '/v4/models',
                    headers=self._client._get_headers(),
                    json=model_meta,
                    verify=False
                )
        model_details = self._handle_response(202, u'creating new model', creation_response)
        model_uid = model_details['metadata']['guid']
        return self.get_details(model_uid)

    def _store_autoAI_model(self,model_path, meta_props, training_data=None, training_target=None,version=False,artifactId=None,subtrainingId=None):
        """
                Store trained model from object storage into Watson Machine Learning repository on IBM Cloud
        """
        model_meta = self.ConfigurationMetaNames._generate_resource_metadata(
            meta_props,
            client=self._client
        )
        self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.NAME, STR_TYPE, True)

        x = re.search(r"[0-9A-Za-z-]+", model_path)
        model_uid = x.group()
        details = self._client.training.get_details(model_uid)


        model_meta.update({"import": details["entity"]["results_reference"]})
        model_meta["import"]["location"]["path"] = model_path
        runtime_uid = 'hybrid_0.1'
        model_type = 'wml-hybrid_0.1'

        # print("model_meta b4" + str(model_meta))


        if self.ConfigurationMetaNames.TYPE not in meta_props:
            model_meta.update({"type": model_type})

        if self.ConfigurationMetaNames.RUNTIME_UID not in meta_props:
            model_meta.update({"runtime": {"href": "/v4/runtimes/"+runtime_uid}})

        # print("model_meta after" + str(model_meta))

        if not self._ICP:
                creation_response = requests.post(
                       self._wml_credentials['url'] + '/v4/models',
                       headers=self._client._get_headers(),
                       json=model_meta
                )
        else:
                creation_response = requests.post(
                    self._wml_credentials['url'] + '/v4/models',
                    headers=self._client._get_headers(),
                    json=model_meta,
                    verify=False
                )
        model_details = self._handle_response(202, u'creating new model', creation_response)
        model_uid = model_details['metadata']['guid']
        return self.get_details(model_uid)


    def _publish_from_file(self, model, meta_props=None, training_data=None, training_target=None,ver=False,artifactid=None):
        """
        Store saved model into Watson Machine Learning repository on IBM Cloud
        """
        if(ver==True):
            #check if artifactid is passed
            Models._validate_type(str_type_conv(artifactid), 'model_uid', STR_TYPE, True)
            return self._publish_from_archive(model, meta_props,version=ver,artifactid=artifactid)
        def is_xml(model_filepath):
            if (os.path.splitext(os.path.basename(model_filepath))[-1] == '.pmml'):
                raise WMLClientError('The file name has an unsupported extension. Rename the file with a .xml extension.')
            return os.path.splitext(os.path.basename(model_filepath))[-1] == '.xml'

        self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.NAME, STR_TYPE, True)

        import tarfile
        import zipfile

        model_filepath = model
        if os.path.isdir(model):
            # TODO this part is ugly, but will work. In final solution this will be removed
            if "tensorflow" in meta_props[self.ConfigurationMetaNames.TYPE]:
                # TODO currently tar.gz is required for tensorflow - the same ext should be supported for all frameworks
                if os.path.basename(model) == '':
                    model = os.path.dirname(model)
                filename = os.path.basename(model) + '.tar.gz'
                current_dir = os.getcwd()
                os.chdir(model)
                target_path = os.path.dirname(model)

                with tarfile.open(os.path.join('..', filename), mode='w:gz') as tar:
                    tar.add('.')

                os.chdir(current_dir)
                model_filepath = os.path.join(target_path, filename)
                if tarfile.is_tarfile(model_filepath) or zipfile.is_zipfile(model_filepath) or is_xml(model_filepath):
                    return self._publish_from_archive(model_filepath, meta_props)
            else:
                self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.TYPE, STR_TYPE, True)
                if ('caffe' in meta_props[self.ConfigurationMetaNames.TYPE]):
                    raise WMLClientError(u'Invalid model file path  specified for: \'{}\'.'.format(meta_props[self.ConfigurationMetaNames.TYPE]))

                loaded_model = load_model_from_directory(meta_props[self.ConfigurationMetaNames.TYPE], model)

                saved_model = self._publish_from_object(loaded_model, meta_props, training_data, training_target)

                return saved_model

        elif is_xml(model_filepath):
            try:
                if self.ConfigurationMetaNames.SPACE_UID in meta_props:
                    self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.SPACE_UID, STR_TYPE, False)
                    meta_props[self._client.repository.ModelMetaNames.SPACE_UID] = {"href": API_VERSION + SPACES + "/" + meta_props[self._client.repository.ModelMetaNames.SPACE_UID]}

                if self.ConfigurationMetaNames.RUNTIME_UID in meta_props:
                    self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.RUNTIME_UID, STR_TYPE, False)
                    meta_props[self._client.repository.ModelMetaNames.RUNTIME_UID] = {"href": API_VERSION + RUNTIMES + "/" + meta_props[self._client.repository.ModelMetaNames.RUNTIME_UID]}

                if self.ConfigurationMetaNames.TRAINING_LIB_UID in meta_props:
                    self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.TRAINING_LIB_UID, STR_TYPE, False)
                    meta_props[self._client.repository.ModelMetaNames.TRAINING_LIB_UID] = {"href": API_VERSION + LIBRARIES + "/" + meta_props[self._client.repository.ModelMetaNames.TRAINING_LIB_UID]}
                if self.ConfigurationMetaNames.PIPELINE_UID in meta_props:
                    self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.PIPELINE_UID, STR_TYPE, False)
                    meta_props[self._client.repository.ModelMetaNames.PIPELINE_UID] = {"href": API_VERSION + PIPELINES + "/" + meta_props[self._client.repository.ModelMetaNames.PIPELINE_UID]}
                meta_data = MetaProps(self._client.repository._meta_props_to_repository_v3_style(meta_props))

                model_artifact = MLRepositoryArtifact(str(model_filepath), name=str(meta_props[self.ConfigurationMetaNames.NAME]), meta_props=meta_data)
                saved_model = self._client.repository._ml_repository_client.models.save(model_artifact)
            except Exception as e:
                raise WMLClientError(u'Publishing model failed.', e)
            else:
                return self.get_details(saved_model.uid)
        elif tarfile.is_tarfile(model_filepath) or zipfile.is_zipfile(model_filepath):
            return self._publish_from_archive(model, meta_props)
        else:
            raise WMLClientError(u'Saving trained model in repository failed. \'{}\' file does not have valid format'.format(model_filepath))

    # TODO make this way when all frameworks will be supported
    # def _publish_from_archive(self, path_to_archive, meta_props=None):
    #     self._validate_meta_prop(meta_props, self.ModelMetaNames.FRAMEWORK_NAME, STR_TYPE, True)
    #     self._validate_meta_prop(meta_props, self.ModelMetaNames.FRAMEWORK_VERSION, STR_TYPE, True)
    #     self._validate_meta_prop(meta_props, self.ModelMetaNames.NAME, STR_TYPE, True)
    #
    #     try:
    #     try:
    #         meta_data = MetaProps(Repository._meta_props_to_repository_v3_style(meta_props))
    #
    #         model_artifact = MLRepositoryArtifact(path_to_archive, name=str(meta_props[self.ModelMetaNames.NAME]), meta_props=meta_data)
    #
    #         saved_model = self._ml_repository_client.models.save(model_artifact)
    #     except Exception as e:
    #         raise WMLClientError(u'Publishing model failed.', e)
    #     else:
    #         return self.get_details(u'{}'.format(saved_model.uid))
    def _create_mode_payload(self,meta_props):
        payload = {
            "name": meta_props[self.ConfigurationMetaNames.NAME],
        }
        if self.ConfigurationMetaNames.TAGS in meta_props:
            self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.TAGS, list, False)
            payload.update({self.ConfigurationMetaNames.TAGS: meta_props[self.ConfigurationMetaNames.TAGS]})

        if self.ConfigurationMetaNames.SPACE_UID in meta_props:
            self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.SPACE_UID, STR_TYPE, False)
            payload.update({self.ConfigurationMetaNames.SPACE_UID: {
                "href": API_VERSION + SPACES + "/" + meta_props[self._client.repository.ModelMetaNames.SPACE_UID]}})

        if self.ConfigurationMetaNames.RUNTIME_UID in meta_props:
            self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.RUNTIME_UID, STR_TYPE, False)
            payload.update({self.ConfigurationMetaNames.RUNTIME_UID: {
                "href": API_VERSION + RUNTIMES + "/" + meta_props[self._client.repository.ModelMetaNames.RUNTIME_UID]}})

        if self.ConfigurationMetaNames.PIPELINE_UID in meta_props:
            self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.PIPELINE_UID, STR_TYPE, False)
            payload.update({self.ConfigurationMetaNames.PIPELINE_UID: {
                "href": API_VERSION + PIPELINES + "/" + meta_props[
                    self._client.repository.ModelMetaNames.PIPELINE_UID]}})

        if self.ConfigurationMetaNames.TRAINING_LIB_UID in meta_props:
            self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.TRAINING_LIB_UID, STR_TYPE, False)
            payload.update({self.ConfigurationMetaNames.TRAINING_LIB_UID: {
                "href": API_VERSION + LIBRARIES + "/" + meta_props[
                    self._client.repository.ModelMetaNames.TRAINING_LIB_UID]}})

        if self.ConfigurationMetaNames.DESCRIPTION in meta_props:
            payload.update({'description': meta_props[self.ConfigurationMetaNames.DESCRIPTION]})

        if self.ConfigurationMetaNames.LABEL_FIELD in meta_props:
            payload.update({'label_column': json.loads(meta_props[self.ConfigurationMetaNames.LABEL_FIELD])})

        if self.ConfigurationMetaNames.TYPE in meta_props:
            payload.update({'type': meta_props[self.ConfigurationMetaNames.TYPE]})

        if self.ConfigurationMetaNames.TRAINING_DATA_REFERENCES in meta_props:
            payload.update(
                {'training_data_references': meta_props[self.ConfigurationMetaNames.TRAINING_DATA_REFERENCES]})

        if self.ConfigurationMetaNames.IMPORT in meta_props:
            payload.update({'import': meta_props[self.ConfigurationMetaNames.IMPORT]})
        if self.ConfigurationMetaNames.CUSTOM in meta_props:
            payload.update({'custom': meta_props[self.ConfigurationMetaNames.CUSTOM]})
        if self.ConfigurationMetaNames.DOMAIN in meta_props:
            payload.update({'domain': meta_props[self.ConfigurationMetaNames.DOMAIN]})

        if self.ConfigurationMetaNames.HYPER_PARAMETERS in meta_props:
            payload.update({'hyper_parameters': meta_props[self.ConfigurationMetaNames.HYPER_PARAMETERS]})
        if self.ConfigurationMetaNames.METRICS in meta_props:
            payload.update({'metrics': meta_props[self.ConfigurationMetaNames.METRICS]})

        if self.ConfigurationMetaNames.INPUT_DATA_SCHEMA in meta_props and self.ConfigurationMetaNames.OUTPUT_DATA_SCHEMA in meta_props:
            self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.INPUT_DATA_SCHEMA, dict, False)
            self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.OUTPUT_DATA_SCHEMA, dict, False)

            payload.update({"schemas": {
                "input": [meta_props[self.ConfigurationMetaNames.INPUT_DATA_SCHEMA]],
                "output": [meta_props[self.ConfigurationMetaNames.OUTPUT_DATA_SCHEMA]]
            }
            })
        return payload

    def _publish_from_archive(self, path_to_archive, meta_props=None,version=False,artifactid=None):
        self._validate_meta_prop(meta_props, self.ConfigurationMetaNames.NAME, STR_TYPE, True)
        def is_xml(model_filepath):
            return os.path.splitext(os.path.basename(model_filepath))[-1] == '.xml'

        url = self._href_definitions.get_published_models_href()
        payload = self._create_mode_payload(meta_props)

        if(version==True):
            if not self._ICP:
                response = requests.put(
                    url+"/"+str_type_conv(artifactid),
                    json=payload,
                    headers=self._client._get_headers()
                )
            else:
                response = requests.put(
                    url+"/"+str_type_conv(artifactid),
                    json=payload,
                    headers=self._client._get_headers(),
                    verify=False
                )


        else:

            if not self._ICP:
                response = requests.post(
                    url,
                    json=payload,
                    headers=self._client._get_headers()
                )
            else:
                response = requests.post(
                    url,
                    json=payload,
                    headers=self._client._get_headers(),
                    verify=False
                )

        result = self._handle_response(201, u'creating model', response)
        model_uid = self._get_required_element_from_dict(result, 'model_details', ['metadata', 'guid'])
        url = self._href_definitions.get_published_model_href(model_uid)+"/content"
        with open(path_to_archive, 'rb') as f:
            if is_xml(path_to_archive):
                if not self._ICP:
                    response = requests.put(
                       url,
                       data=f,
                       headers=self._client._get_headers(content_type='application/xml')
                    )
                else:
                    response = requests.put(
                        url,
                        data=f,
                        headers=self._client._get_headers(content_type='application/xml'),
                        verify=False
                    )
            else:
                if not self._ICP:
                    response = requests.put(
                        url,
                        data=f,
                        headers=self._client._get_headers(content_type='application/octet-stream')
                    )
                else:
                    response = requests.put(
                        url,
                        data=f,
                        headers=self._client._get_headers(content_type='application/octet-stream'),
                        verify=False
                    )

            self._handle_response(200, u'uploading model content', response, False)
            if(version==True):
                return self._client.repository.get_details(artifactid+"/versions/"+model_uid)
            return self.get_details(model_uid)
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def store(self, model, meta_props=None, training_data=None, training_target=None, pipeline=None,version=False,artifactid=None, feature_names=None, label_column_names=None,subtrainingId=None):
        """
        Store trained model into Watson Machine Learning repository on Cloud.

        :param model:  The train model object (e.g: spark PipelineModel), or path to saved model in format .tar.gz/.str/.xml or directory containing model file(s), or trained model guid
        :type model: object/{str_type}

        :param meta_props: meta data of the training definition. To see available meta names use:

            >>> client.models.ConfigurationMetaNames.get()

        :type meta_props: dict/{str_type}

        :param training_data:  Spark DataFrame supported for spark models. Pandas dataframe, numpy.ndarray or array supported for scikit-learn models
        :type training_data: spark dataframe, pandas dataframe, numpy.ndarray or array

        :param training_target: array with labels required for scikit-learn models
        :type training_target: array

        :param pipeline: pipeline required for spark mllib models
        :type training_target: object

        :returns: stored model details
        :rtype: dict

        The most simple use is:

        >>> stored_model_details = client.models.store(model, name)

        In more complicated cases you should create proper metadata, similar to this one:

        >>> metadata = {
        >>>        client.repository.ModelMetaNames.NAME: 'customer satisfaction prediction model',
        >>>        client.repository.ModelMetaNames.FRAMEWORK_NAME: 'tensorflow',
        >>>        client.repository.ModelMetaNames.FRAMEWORK_VERSION: '1.5',
        >>>        client.repository.ModelMetaNames.RUNTIME_NAME: 'python',
        >>>        client.repository.ModelMetaNames.RUNTIME_VERSION: '3.5'
        >>>}

        where FRAMEWORK_NAME may be one of following: "spss-modeler", "tensorflow", "xgboost", "scikit-learn", "pmml".

        A way you might use me with local tar.gz containing model:

        >>> stored_model_details = client.models.store(path_to_tar_gz, meta_props=metadata, training_data=None)

        A way you might use me with local directory containing model file(s):

        >>> stored_model_details = client.models.store(path_to_model_directory, meta_props=metadata, training_data=None)

        A way you might use me with trained model guid:

        >>> stored_model_details = client.models.store(trained_model_guid, meta_props=metadata, training_data=None)
        """
        model = str_type_conv(model)
        Models._validate_type(model, u'model', object, True)
        meta_props = copy.deepcopy(meta_props)
        meta_props = str_type_conv(meta_props)  # meta_props may be str, in this situation for py2 it will be converted to unicode
        Models._validate_type(meta_props, u'meta_props', [dict, STR_TYPE], True)
        # Repository._validate_type(training_data, 'training_data', object, False)
        # Repository._validate_type(training_target, 'training_target', list, False)
        meta_props_str_conv(meta_props)

        if type(meta_props) is STR_TYPE:
            meta_props = {
                self.ConfigurationMetaNames.NAME: meta_props
            }



        #self.ConfigurationMetaNames._validate(meta_props)

        if ("frameworkName" in meta_props):
         framework_name = meta_props["frameworkName"].lower()
         if version == True and (framework_name == "mllib" or framework_name == "wml"):
            raise WMLClientError(u'Unsupported framework name: \'{}\' for creating a model version'.format(framework_name))


        if not isinstance(model, STR_TYPE):
            if(version==True):
                raise WMLClientError(u'Unsupported type: object for param model. Supported types: path to saved model, training ID')
            else:
                saved_model = self._publish_from_object(model=model, meta_props=meta_props, training_data=training_data, training_target=training_target, pipeline=pipeline, feature_names=feature_names, label_column_names=label_column_names)
        else:
            # print("model is a string type")
            if (model.endswith('.pickle') and os.path.sep in model):
                # AUTO AI Trained model
                saved_model = self._store_autoAI_model(model_path=model, meta_props=meta_props, training_data=training_data, training_target=training_target, version=version, artifactId=artifactid, subtrainingId=subtrainingId)

            elif (os.path.sep in model) or os.path.isfile(model) or os.path.isdir(model):
                if not os.path.isfile(model) and not os.path.isdir(model):
                    raise WMLClientError(u'Invalid path: neither file nor directory exists under this path: \'{}\'.'.format(model))
                saved_model = self._publish_from_file(model=model, meta_props=meta_props, training_data=training_data, training_target=training_target,ver=version,artifactid=artifactid)
            else:
                 saved_model = self._publish_from_training(model_uid=model, meta_props=meta_props, training_data=training_data, training_target=training_target,version=version,artifactId=artifactid, subtrainingId=subtrainingId)

        return saved_model

    def update(self, model_uid, meta_props=None):
        """
            Update metadata of model.

            :param model_uid:  Model UID
            :type model_uid: str

            :returns: updated metadata of model
            :rtype: dict

            A way you might use me is:

            >>> model_details = client.models.update(model_uid, content_path)
        """
        Models._validate_type(model_uid, 'model_uid', STR_TYPE, True)
        Models._validate_type(meta_props, 'meta_props', dict, True)

        if meta_props is not None: # TODO
            #raise WMLClientError('Meta_props update unsupported.')
            self._validate_type(meta_props, u'meta_props', dict, True)
            meta_props_str_conv(meta_props)

            url = self._href_definitions.get_published_model_href(model_uid)

            if not self._ICP:
                response = requests.get(
                    url,
                    headers=self._client._get_headers()
                )
            else:
                response = requests.get(
                    url,
                    headers=self._client._get_headers(),
                    verify=False
                )

            details = response.json()

            # with validation should be somewhere else, on the begining, but when patch will be possible
            patch_payload = self.ConfigurationMetaNames._generate_patch_payload(details['entity'], meta_props, with_validation=True)
            if not self._ICP:
                response_patch = requests.patch(url, json=patch_payload, headers=self._client._get_headers())
            else:
                response_patch = requests.patch(url, json=patch_payload, headers=self._client._get_headers(),verify=False)
            updated_details = self._handle_response(200, u'model version patch', response_patch)
            return updated_details

        return self.get_details(model_uid)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def load(self, artifact_uid):
        """
        Load model from repository to object in local environment.

        :param artifact_uid:  stored model UID
        :type artifact_uid: {str_type}

        :returns: trained model
        :rtype: object

        A way you might use me is:

        >>> model = client.models.load(model_uid)
        """
        artifact_uid = str_type_conv(artifact_uid)
        Models._validate_type(artifact_uid, u'artifact_uid', STR_TYPE, True)

        try:
            loaded_model = self._client.repository._ml_repository_client.models.get(artifact_uid)
            loaded_model = loaded_model.model_instance()
            self._logger.info(u'Successfully loaded artifact with artifact_uid: {}'.format(artifact_uid))
            return loaded_model
        except Exception as e:
            raise WMLClientError(u'Loading model with artifact_uid: \'{}\' failed.'.format(artifact_uid), e)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def download(self, model_uid, filename='downloaded_model.tar.gz'):
        """
            Download model from repository to local file.

            :param model_uid: stored model UID
            :type model_uid: {str_type}

            :param filename: name of local file to create (optional)
            :type filename: {str_type}


            A way you might use me is:

            >>> client.models.download(model_uid, 'my_model.tar.gz')
        """
        if os.path.isfile(filename):
            raise WMLClientError(u'File with name: \'{}\' already exists.'.format(filename))

        model_uid = str_type_conv(model_uid)
        Models._validate_type(model_uid, u'model_uid', STR_TYPE, True)
        filename = str_type_conv(filename)
        Models._validate_type(filename, u'filename', STR_TYPE, True)

        artifact_url = self._href_definitions.get_model_last_version_href(model_uid)

        try:
            artifact_content_url = str(artifact_url + u'/content')
            if not self._ICP:
                r = requests.get(artifact_content_url, headers=self._client._get_headers(), stream=True)
            else:
                r = requests.get(artifact_content_url, headers=self._client._get_headers(), stream=True, verify=False)
            self._handle_response(200, 'downloading model', r, False)

            downloaded_model = r.content
            self._logger.info(u'Successfully downloaded artifact with artifact_url: {}'.format(artifact_url))
        except WMLClientError as e:
            raise e
        except Exception as e:
            raise WMLClientError(u'Downloading model with artifact_url: \'{}\' failed.'.format(artifact_url), e)

        try:
            with open(filename, 'wb') as f:
                f.write(downloaded_model)
            print(u'Successfully saved model content to file: \'{}\''.format(filename))
            return os.getcwd() + "/"+filename
        except IOError as e:
            raise WMLClientError(u'Saving model with artifact_url: \'{}\' failed.'.format(filename), e)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def delete(self, model_uid):
        """
            Delete model from repository.

            :param model_uid: stored model UID
            :type model_uid: {str_type}

            A way you might use me is:

            >>> client.models.delete(model_uid)
        """
        model_uid = str_type_conv(model_uid)
        Models._validate_type(model_uid, u'model_uid', STR_TYPE, True)

        model_endpoint = self._href_definitions.get_published_model_href(model_uid)
        self._logger.debug(u'Deletion artifact model endpoint: {}'.format(model_endpoint))
        if not self._ICP:
            response_delete = requests.delete(model_endpoint, headers=self._client._get_headers())
        else:
            response_delete = requests.delete(model_endpoint, headers=self._client._get_headers(), verify=False)
        return self._handle_response(204, u'model deletion', response_delete, False)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_details(self, model_uid=None, limit=None):
        """
           Get metadata of stored models. If model uid is not specified returns all models metadata.

           :param model_uid: stored model, definition or pipeline UID (optional)
           :type model_uid: {str_type}

           :param limit: limit number of fetched records (optional)
           :type limit: int

           :returns: stored model(s) metadata
           :rtype: dict

           A way you might use me is:

           >>> model_details = client.models.get_details(model_uid)
           >>> models_details = client.models.get_details()
        """
        model_uid = str_type_conv(model_uid)
        Models._validate_type(model_uid, u'model_uid', STR_TYPE, False)
        Models._validate_type(limit, u'limit', int, False)

        if not self._ICP:
            url = self._href_definitions.get_published_models_href()
        else:
            url = self._href_definitions.get_published_models_href()
        return self._get_artifact_details(url, model_uid, limit, 'models')

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_href(model_details):
        """
            Get url of stored model.

            :param model_details:  stored model details
            :type model_details: dict

            :returns: url to stored model
            :rtype: {str_type}

            A way you might use me is:

            >>> model_url = client.models.get_href(model_details)
        """
        Models._validate_type(model_details, u'model_details', object, True)
        Models._validate_type_of_details(model_details, MODEL_DETAILS_TYPE)


        return WMLResource._get_required_element_from_dict(model_details, u'model_details', [u'metadata', u'href'])

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_uid(model_details):
        """
            Get uid of stored model.

            :param model_details:  stored model details
            :type model_details: dict

            :returns: uid of stored model
            :rtype: {str_type}

            A way you might use me is:

            >>> model_uid = client.models.get_uid(model_details)
        """
        Models._validate_type(model_details, u'model_details', object, True)
        Models._validate_type_of_details(model_details, MODEL_DETAILS_TYPE)


        return WMLResource._get_required_element_from_dict(model_details, u'model_details', [u'metadata', u'guid'])

    def list(self, limit=None):
        """
           List stored models. If limit is set to None there will be only first 50 records shown.

           :param limit: limit number of fetched records (optional)
           :type limit: int

           A way you might use me is

           >>> client.models.list()
        """

        model_resources = self.get_details(limit=limit)[u'resources']
        model_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at'], m[u'entity'][u'type']) for m in model_resources]

        self._list(model_values, [u'GUID', u'NAME', u'CREATED', u'TYPE'], limit, _DEFAULT_LIST_LENGTH)

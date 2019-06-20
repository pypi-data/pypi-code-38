
import unittest
import os
from configparser import ConfigParser
import json
from sklearn import datasets
from sklearn.pipeline import Pipeline
from sklearn import preprocessing
from sklearn import svm
from importlib import reload
import site
from watson_machine_learning_client.log_util import get_logger
from watson_machine_learning_client.wml_client_error import *


if "ENV" in os.environ:
    environment = os.environ['ENV']
else:
    environment = "SVT"


class TestRepository(unittest.TestCase):
    logger = get_logger(__name__)

    published_tf_local_model_details = None
    published_sklearn_object_model_details = None
    model_tf_local_uid = None
    model_tf_local_url = None
    model_sklearn_object_uid = None
    model_sklearn_object_url = None

    @classmethod
    def setUpClass(self):
        TestRepository.logger.info("Service Instance: setting up credentials")
        config = ConfigParser()
        config.read('../config.ini')
        self.wml_credentials = json.loads(config.get(environment, 'wml_credentials'))
        self.wml_lib = __import__('watson_machine_learning_client', globals(), locals())
        self.client = self.wml_lib.WatsonMachineLearningAPIClient(self.wml_credentials)
        self.model_path = os.path.join(os.getcwd(), 'artifacts', 'tf-saved_model.tar.gz')

    def test_01_store_local_tf_model(self):
        TestRepository.logger.info("Saving trained model in repo ...")
        TestRepository.logger.debug(self.model_path)
        model_meta_props = {self.client.repository.ModelMetaNames.NAME: "my_description",
                            self.client.repository.ModelMetaNames.AUTHOR_NAME: "John Smith",
                            self.client.repository.ModelMetaNames.AUTHOR_EMAIL: "js@js.com",
                            self.client.repository.ModelMetaNames.FRAMEWORK_NAME: "tensorflow",
                            self.client.repository.ModelMetaNames.FRAMEWORK_VERSION: "1.5",
                            self.client.repository.ModelMetaNames.RUNTIME_NAME: "python",
                            self.client.repository.ModelMetaNames.RUNTIME_VERSION: "3.5"}
        TestRepository.published_tf_local_model_details = self.client.repository.store_model(model=self.model_path, name="Local TF sample model", meta_props=model_meta_props)

        self.assertIsNotNone(TestRepository.published_tf_local_model_details)

    def test_01_store_sklearn_object_model(self):
        TestRepository.logger.info("Creating scikit-learn model ...")
        global digits
        digits = datasets.load_digits()
        scaler = preprocessing.StandardScaler()
        clf = svm.SVC(kernel='rbf')
        pipeline = Pipeline([('scaler', scaler), ('svc', clf)])
        global model
        model = pipeline.fit(digits.data, digits.target)
        predicted = model.predict(digits.data[1: 10])

        TestRepository.logger.debug(predicted)
        self.assertIsNotNone(predicted)

        self.logger.info("Publishing scikit-learn model ...")
        model_props = {self.client.repository.ModelMetaNames.AUTHOR_NAME: "IBM",
                       self.client.repository.ModelMetaNames.AUTHOR_EMAIL: "ibm@ibm.com"}
        model_name = "LOCALLY created Digits prediction model"
        TestRepository.published_sklearn_object_model_details = self.client.repository.store_model(model=model, name=model_name, meta_props=model_props, training_data=digits.data, training_target=digits.target)
        self.assertIsNotNone(TestRepository.published_sklearn_object_model_details)

    def test_01_store_sklearn_object_model_without_meta(self):
        TestRepository.logger.info("Creating scikit-learn model ...")
        global digits
        digits = datasets.load_digits()
        scaler = preprocessing.StandardScaler()
        clf = svm.SVC(kernel='rbf')
        pipeline = Pipeline([('scaler', scaler), ('svc', clf)])
        global model
        model = pipeline.fit(digits.data, digits.target)
        predicted = model.predict(digits.data[1: 10])

        TestRepository.logger.debug(predicted)
        self.assertIsNotNone(predicted)

        self.logger.info("Publishing scikit-learn model without meta props...")
        model_name = "LOCALLY created Digits prediction model"
        model_details = self.client.repository.store_model(model=model, name=model_name, meta_props=None, training_data=digits.data, training_target=digits.target)
        self.assertIsNotNone(model_details)

    def test_01_store_model_none_model(self):
        TestRepository.logger.info("Saving none model in repo ...")
        TestRepository.logger.debug(self.model_path)
        model_meta_props = {self.client.repository.ModelMetaNames.NAME: "my_description",
                            self.client.repository.ModelMetaNames.AUTHOR_NAME: "John Smith",
                            self.client.repository.ModelMetaNames.AUTHOR_EMAIL: "js@js.com",
                            self.client.repository.ModelMetaNames.FRAMEWORK_NAME: "tensorflow",
                            self.client.repository.ModelMetaNames.FRAMEWORK_VERSION: "1.5",
                            self.client.repository.ModelMetaNames.RUNTIME_NAME: "python",
                            self.client.repository.ModelMetaNames.RUNTIME_VERSION: "3.5"}
        model_details = self.client.repository.store_model(model=None, name="Local TF sample model", meta_props=model_meta_props)
        self.assertIsNone(model_details)

    def test_01_store_model_empty_model(self):
        TestRepository.logger.info("Saving empty trained model in repo ...")
        TestRepository.logger.debug(self.model_path)
        model_meta_props = {self.client.repository.ModelMetaNames.NAME: "my_description",
                            self.client.repository.ModelMetaNames.AUTHOR_NAME: "John Smith",
                            self.client.repository.ModelMetaNames.AUTHOR_EMAIL: "js@js.com",
                            self.client.repository.ModelMetaNames.FRAMEWORK_NAME: "tensorflow",
                            self.client.repository.ModelMetaNames.FRAMEWORK_VERSION: "1.5",
                            self.client.repository.ModelMetaNames.RUNTIME_NAME: "python",
                            self.client.repository.ModelMetaNames.RUNTIME_VERSION: "3.5"}

        with self.assertRaises(WMLClientError) as context:
            self.client.repository.store_model(model="", name="Local TF sample model", meta_props=model_meta_props)

        self.assertIn("Invalid uid", str(context.exception))


    def test_01_store_model_invalid_path(self):
        TestRepository.logger.info("Saving empty trained model in repo ...")
        TestRepository.logger.debug(self.model_path)
        model_meta_props = {self.client.repository.ModelMetaNames.NAME: "my_description",
                            self.client.repository.ModelMetaNames.AUTHOR_NAME: "John Smith",
                            self.client.repository.ModelMetaNames.AUTHOR_EMAIL: "js@js.com",
                            self.client.repository.ModelMetaNames.FRAMEWORK_NAME: "tensorflow",
                            self.client.repository.ModelMetaNames.FRAMEWORK_VERSION: "1.5",
                            self.client.repository.ModelMetaNames.RUNTIME_NAME: "python",
                            self.client.repository.ModelMetaNames.RUNTIME_VERSION: "3.5"}

        with self.assertRaises(WMLClientError) as context:
            self.client.repository.store_model(model="/home/Downloads/model.tar", name="Local TF sample model", meta_props=model_meta_props)

        self.assertIn("Invalid uid", str(context.exception))

    def test_01_store_model_json_model(self):
        TestRepository.logger.info("Saving empty json trained model in repo ...")
        TestRepository.logger.debug(self.model_path)
        model_meta_props = {self.client.repository.ModelMetaNames.NAME: "my_description",
                            self.client.repository.ModelMetaNames.AUTHOR_NAME: "John Smith",
                            self.client.repository.ModelMetaNames.AUTHOR_EMAIL: "js@js.com",
                            self.client.repository.ModelMetaNames.FRAMEWORK_NAME: "tensorflow",
                            self.client.repository.ModelMetaNames.FRAMEWORK_VERSION: "1.5",
                            self.client.repository.ModelMetaNames.RUNTIME_NAME: "python",
                            self.client.repository.ModelMetaNames.RUNTIME_VERSION: "3.5"}

        with self.assertRaises(WMLClientError) as context:
            self.client.repository.store_model(model="{}", name="Local TF sample model", meta_props=model_meta_props)

        self.assertIn("Invalid uid", str(context.exception))

    def test_01_store_model_none_name(self):
        TestRepository.logger.info("Saving trained model with None name in repo ...")
        TestRepository.logger.debug(self.model_path)
        model_meta_props = {self.client.repository.ModelMetaNames.NAME: "my_description",
                            self.client.repository.ModelMetaNames.AUTHOR_NAME: "John Smith",
                            self.client.repository.ModelMetaNames.AUTHOR_EMAIL: "js@js.com",
                            self.client.repository.ModelMetaNames.FRAMEWORK_NAME: "tensorflow",
                            self.client.repository.ModelMetaNames.FRAMEWORK_VERSION: "1.5",
                            self.client.repository.ModelMetaNames.RUNTIME_NAME: "python",
                            self.client.repository.ModelMetaNames.RUNTIME_VERSION: "3.5"}

        with self.assertRaises(WMLClientError) as context:
            self.client.repository.store_model(model=self.model_path, name=None, meta_props=model_meta_props)

        self.assertIn("Invalid input", str(context.exception))

    def test_01_store_model_empty_name(self):
        TestRepository.logger.info("Saving trained model with empty name in repo ...")
        TestRepository.logger.debug(self.model_path)
        model_meta_props = {self.client.repository.ModelMetaNames.NAME: "my_description",
                            self.client.repository.ModelMetaNames.AUTHOR_NAME: "John Smith",
                            self.client.repository.ModelMetaNames.AUTHOR_EMAIL: "js@js.com",
                            self.client.repository.ModelMetaNames.FRAMEWORK_NAME: "tensorflow",
                            self.client.repository.ModelMetaNames.FRAMEWORK_VERSION: "1.5",
                            self.client.repository.ModelMetaNames.RUNTIME_NAME: "python",
                            self.client.repository.ModelMetaNames.RUNTIME_VERSION: "3.5"}

        with self.assertRaises(WMLClientError) as context:
            self.client.repository.store_model(model=self.model_path, name="", meta_props=model_meta_props)

        self.assertIn("Invalid input", str(context.exception))

    def test_01_store_model_json_name(self):
        TestRepository.logger.info("Saving trained model with empty json name in repo ...")
        TestRepository.logger.debug(self.model_path)
        model_meta_props = {self.client.repository.ModelMetaNames.NAME: "my_description",
                            self.client.repository.ModelMetaNames.AUTHOR_NAME: "John Smith",
                            self.client.repository.ModelMetaNames.AUTHOR_EMAIL: "js@js.com",
                            self.client.repository.ModelMetaNames.FRAMEWORK_NAME: "tensorflow",
                            self.client.repository.ModelMetaNames.FRAMEWORK_VERSION: "1.5",
                            self.client.repository.ModelMetaNames.RUNTIME_NAME: "python",
                            self.client.repository.ModelMetaNames.RUNTIME_VERSION: "3.5"}

        with self.assertRaises(WMLClientError) as context:
            self.client.repository.store_model(model=self.model_path, name="{}", meta_props=model_meta_props)

        self.assertIn("Invalid input", str(context.exception))

    def test_02_get_local_tf_model_uid(self):
        TestRepository.model_tf_local_uid = self.client.repository.get_model_uid(TestRepository.published_tf_local_model_details)
        TestRepository.logger.info("Published model ID:" + str(TestRepository.model_tf_local_uid))
        self.assertIsNotNone(TestRepository.model_tf_local_uid)

    def test_02_get_sklearn_object_model_uid(self):
        TestRepository.model_sklearn_object_uid = self.client.repository.get_model_uid(TestRepository.published_sklearn_object_model_details)
        TestRepository.logger.info("Published model ID:" + str(TestRepository.model_sklearn_object_uid))
        self.assertIsNotNone(TestRepository.model_sklearn_object_uid)

    def test_02_get_model_uid_none_details(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_model_uid(model_details=None)
        self.assertIn("provided", str(context.exception))

    def test_02_get_model_uid_empty_details(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_model_uid(model_details="")
        self.assertIn("Unexpected type", str(context.exception))

    def test_02_get_model_uid_empty_dict_details(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_model_uid(model_details={})
        self.assertIn("provided", str(context.exception))

    def test_02_get_model_uid_fake_dict_details(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_model_uid(model_details={'model_details': 'metadata'})
        self.assertIn("provided", str(context.exception))

    def test_02_get_model_uid_no_details(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_model_uid()
        self.assertIn("Invalid", str(context.exception))

    def test_03_get_local_tf_model_url(self):
        TestRepository.model_tf_local_url = self.client.repository.get_model_url(TestRepository.published_tf_local_model_details)
        TestRepository.logger.info("Published model ID:" + str(TestRepository.model_tf_local_url))
        self.assertIsNotNone(TestRepository.model_tf_local_url)

    def test_03_get_sklearn_object_model_url(self):
        TestRepository.model_sklearn_object_url = self.client.repository.get_model_url(TestRepository.published_sklearn_object_model_details)
        TestRepository.logger.info("Published model URL:" + str(TestRepository.model_sklearn_object_url))
        self.assertIsNotNone(TestRepository.model_sklearn_object_url)

    def test_03_get_model_url_none_details(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_model_url(model_details=None)
        self.assertIn("Invalid", str(context.exception))

    def test_03_get_model_url_empty_details(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_model_url(model_details="")
        self.assertIn("Unexpected", str(context.exception))

    def test_03_get_model_url_empty_dict_details(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_model_url(model_details={})
        self.assertIn("provided", str(context.exception))

    def test_03_get_model_url_fake_dict_details(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_model_url(model_details={'model_details' : 'metadata'})
        self.assertIn("provided", str(context.exception))

    def test_03_get_model_url_no_details(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_model_url()
        self.assertIn("Invalid", str(context.exception))

    def test_04_load_local_tf_model_model(self):
        self.assertTrue(self.client.repository.load(TestRepository.model_tf_local_uid))

    def test_04_load_model_no_value(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.load()
        self.assertIn("Both", str(context.exception))

    def test_04_load_model_none_uid(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.load(artifact_uid=None)
        self.assertIn("Both", str(context.exception))

    def test_04_load_model_none_url(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.load(artifact_url=None)
        self.assertIn("Both", str(context.exception))

    def test_04_load_model_none_both(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.load(artifact_uid=None, artifact_url=None)
        self.assertIn("Both", str(context.exception))

    def test_04_load_model_no_exist(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.load(artifact_uid="sjkada7ddnnsdh2dmdn")
        self.assertIn("Invalid", str(context.exception))

    def test_05_get_local_tf_details_uid(self):
        self.assertIsNotNone(self.client.repository.get_details(artifact_uid=TestRepository.model_tf_local_uid))

    def test_05_get_sklearn_object_details_url(self):
        self.assertIsNotNone(self.client.repository.get_details(artifact_url=TestRepository.model_sklearn_object_url))

    def test_05_get_model_details_no_value(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_details()
        self.assertIn("Invalid", str(context.exception))

    def test_05_get_model_details_none_uid(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_details(artifact_uid=None)
        self.assertIn("Invalid", str(context.exception))

    def test_05_get_model_details_none_url(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_details(artifact_url=None)
        self.assertIn("Invalid", str(context.exception))

    def test_05_get_model_details_none_both(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_details(artifact_url=None, artifact_uid=None)
        self.assertIn("Invalid", str(context.exception))

    def test_05_get_model_details_empty_uid(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_details(artifact_uid="")
        self.assertIn("Invalid", str(context.exception))

    def test_05_get_model_details_empty_url(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_details(artifact_url="")
        self.assertIn("Passed url is not valid", str(context.exception))

    def test_05_get_model_details_empty_json_uid(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_details(artifact_uid="{}")
        self.assertIn("Invalid", str(context.exception))

    def test_05_get_model_details_empty_json_url(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_details(artifact_url="{}")
        self.assertIn("Passed url is not valid", str(context.exception))

    def test_06_get_local_tf_model_details(self):
        self.assertIsNotNone(self.client.repository.get_model_details(model_uid=TestRepository.model_tf_local_uid))

    def test_06_get_sklearn_model_details(self):
        self.assertIsNotNone(self.client.repository.get_model_details(model_url=TestRepository.model_sklearn_object_url))

    def test_06_get_model_details_no_values(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_model_details()
        self.assertIn("Invalid", str(context.exception))

    def test_06_get_model_details_none_uid(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_model_details(model_uid=None)
        self.assertIn("Invalid", str(context.exception))

    def test_06_get_model_details_none_url(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_model_details(model_url=None)
        self.assertIn("Invalid", str(context.exception))

    def test_06_get_model_details_empty_uid(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_model_details(model_uid="")
        self.assertIn("Invalid", str(context.exception))

    def test_06_get_model_details_empty_url(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_model_details(model_url="")
        self.assertIn("Invalid", str(context.exception))

    def test_06_get_model_details_empty_json_uid(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_model_details(model_uid="{}")
        self.assertIn("Invalid", str(context.exception))

    def test_06_get_model_details_empty_json_url(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_model_details(model_url="{}")
        self.assertIn("Invalid", str(context.exception))

    def test_06_get_model_details_invalid_uid(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_model_details(model_uid="xdjksa92kdanx202")
        self.assertIn("Invalid", str(context.exception))

    def test_06_get_model_details_invalid_url(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.get_model_details(model_url="/fvt/")
        self.assertIn("Invalid", str(context.exception))

    def test_07_get_local_tf_model_definition_details(self):
        self.assertIsNotNone(self.client.repository.get_definition_details(TestRepository.model_tf_local_uid))

    def test_08_download_sklearn_object_model_url(self):
        self.client.repository.download(artifact_url=TestRepository.model_sklearn_object_url, filename='download_test_url')

    def test_08_download_sklearn_object_model_uid(self):
        self.client.repository.download(artifact_uid=TestRepository.model_sklearn_object_uid, filename='download_test_uid')

    def test_08_download_model_no_values(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.download()
        self.assertIn("Both", str(context.exception))

    def test_08_download_none_uid(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.download(artifact_uid=None, filename='download_none_test_uid')
        self.assertIn("Both", str(context.exception))

    def test_08_download_none_url(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.download(artifact_url=None, filename='download_none_test_url')
        self.assertIn("Both", str(context.exception))

    def test_08_download_none_filename(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.download(artifact_uid=TestRepository.model_sklearn_object_uid, filename=None)
        self.assertIn("Invalid", str(context.exception))

    def test_08_download_empty_uid(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.download(artifact_uid="", filename='download_empty_test_uid')
        self.assertIn("Invalid", str(context.exception))

    def test_08_download_empty_url(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.download(artifact_url="", filename='download_test_uid')
        self.assertIn("Passed url is not valid", str(context.exception))

    def test_08_download_empty_filename(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.download(artifact_uid=TestRepository.model_sklearn_object_uid, filename="")
        self.assertIn("failed", str(context.exception))

    def test_08_download_none_exist_uid(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.download(artifact_uid="sakd8sadk828s", filename='download_test_uid')
        self.assertIn("Invalid", str(context.exception))

    def test_09_delete_local_tf_model(self):
        self.client.repository.delete(artifact_uid=TestRepository.model_tf_local_uid)

    def test_09_delete_sklearn_object_model(self):
        self.client.repository.delete(artifact_url=TestRepository.model_sklearn_object_url)

    def test_09_delete_model_no_values(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.delete()
        self.assertIn("Both", str(context.exception))

    def test_09_delete_model_none_uid(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.delete(artifact_uid=None)
        self.assertIn("Both", str(context.exception))

    def test_09_delete_model_none_url(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.delete(artifact_url=None)
        self.assertIn("Both", str(context.exception))

    def test_09_delete_model_empty_uid(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.delete(artifact_uid="")
        self.assertIn("Invalid", str(context.exception))

    def test_09_delete_model_empty_url(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.delete(artifact_url="")
        self.assertIn("Passed url is not valid", str(context.exception))

    def test_09_delete_model_none_exist_uid(self):
        with self.assertRaises(WMLClientError) as context:
            self.client.repository.delete(artifact_uid="fxjkfd8dskfdn")
        self.assertIn("Invalid", str(context.exception))


if __name__ == '__main__':
    unittest.main()

import requests

from imagine_client_py.utils import normalize_metadata_headers

supported_image_based_models = [
    'phenomenal-face',
    'happy-face',
    'manna',
    'face-detector',
    'food-detector',
]


class ImageBasedModel:
    """
    The :class:`ImageBasedModel <ImageBasedModel>` object
    contains the configuration to access the specified
    model using the Imagine API.
    """

    def __init__(self, client, model_id):

        #: Imagine client
        self.client = client

        #: Name of one of the supported models
        self.model_id = model_id

        #: Input type for the model
        self.model_type = 'image'

        #: Base URL for the Imagine API
        self.base_url = self.client.config['base_url']

        #: Version of the Imagine API
        self.api_version = self.client.config['api_version']

        #: API key for Imagine API
        self.api_key = self.client.config['api_key']

        #: URL for the specified model
        self.model_url = "{0}/{1}/{2}".format(
            self.base_url,
            self.api_version,
            self.model_id
        )

    @staticmethod
    def create(client, model_id):
        """
        Create an ImageBasedModel for a specific model.
        :param client: Imagine client
        :param model_id: Name of a supported model
        :return: ImageBasedModel
        """

        if model_id not in supported_image_based_models:
            raise Exception(
                'Image Model [{0}] is not supported. Supported image models: {1}'.format(
                    model_id,
                    supported_image_based_models
                )
            )

        return ImageBasedModel(client, model_id)

    def _post_label_data(self, data, metatype, metadata=None):
        """
        Insert labeled data into the server-side database
        :param data: Dictionary object of model prediction data
        :param metatype: Type of prediction
        :param metadata: Dictionary object containing Imagine metadata
        :return: Dict
        """

        url = "{0}/label".format(self.model_url)

        if metadata is None:
            metadata = {}

        headers = normalize_metadata_headers(metadata)
        headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'x-imagine-meta-type': metatype,
        })

        response = requests.post(
            url,
            json=data,
            headers=headers
        )

        if response.ok:
            return response.json()
        else:
            raise Exception(
                "Error making request to the /label ({0}) endpoint. Status code {1}".format(
                    metatype,
                    response.status_code
                )
            )

    def infer(self, image_file, store_image=False, metadata=None):
        """
        Generate a prediction using the specified model.
        :param image_file: File object of an image
        :param store_image: Boolean whether to store the image server-side
        :param metadata: Dictionary object containing Imagine metadata
        :return: Dict
        """

        url = "{0}/infer".format(self.model_url)

        if metadata is None:
            metadata = {}

        headers = normalize_metadata_headers(metadata)
        headers['Accept'] = 'application/json'
        
        if self.api_key:
            headers['Authorization'] = 'Bearer {api_key}'.format(api_key=self.api_key)

        response = requests.post(
            url,
            headers=headers,
            files={
                'image': image_file
            },
            data={
                'store': store_image
            }
        )

        if response.ok:
            return response.json()
        else:
            raise Exception(
                "Error making request to the /infer endpoint. Status code {0}".format(
                    response.status_code
                )
            )
    
    def insert_correction(self, corrections_dict, metadata):
        """
        Insert a correction into the server-side 'corrections' database
        :param corrections_dict: Dictionary object of a correction
        :param metadata: Dictionary object containing Imagine metadata
        :return: Dict
        """

        return self._post_label_data(corrections_dict, 'corrections', metadata)

    def insert_prediction(self, predictions_dict, metadata):
        """
        Insert a correction into the server-side 'predictions' database
        :param predictions_dict: Dictionary object of an edge prediction
        :param metadata: Dictionary object containing Imagine metadata
        :return: Dict
        """

        return self._post_label_data(predictions_dict, 'predictions', metadata)

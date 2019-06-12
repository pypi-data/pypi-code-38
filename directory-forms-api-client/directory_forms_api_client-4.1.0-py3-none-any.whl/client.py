from django.conf import settings

from directory_client_core.base import AbstractAPIClient
from directory_forms_api_client.version import __version__


class APIFormsClient(AbstractAPIClient):

    endpoints = {
        'ping': 'api/healthcheck/ping/',
        'submission': 'api/submission/',
    }
    version = __version__

    def ping(self):
        return self.get(url=self.endpoints['ping'])

    def submit_generic(self, data):
        return self.post(url=self.endpoints['submission'], data=data)


forms_api_client = APIFormsClient(
    base_url=settings.DIRECTORY_FORMS_API_BASE_URL,
    api_key=settings.DIRECTORY_FORMS_API_API_KEY,
    sender_id=settings.DIRECTORY_FORMS_API_SENDER_ID,
    timeout=settings.DIRECTORY_FORMS_API_DEFAULT_TIMEOUT,
)

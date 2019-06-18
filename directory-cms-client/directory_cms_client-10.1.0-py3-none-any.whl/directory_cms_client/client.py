import pkg_resources

from directory_client_core.base import AbstractAPIClient
from directory_client_core.helpers import fallback

from django.conf import settings
from django.core.cache import caches


def build_params(
    language_code=None, draft_token=None, fields=None, region=None,
        limit=None, offset=None
):
    params = {'fields': fields or ['*']}
    if language_code:
        params['lang'] = language_code
    if draft_token:
        params['draft_token'] = draft_token
    if region:
        params['region'] = region
    if limit:
        params['limit'] = limit
    if offset:
        params['offset'] = offset
    return params


class DirectoryCMSClient(AbstractAPIClient):
    endpoints = {
        'ping': '/healthcheck/ping/',
        'page-by-type': '/api/pages/lookup-by-type/{page_type}/',
        'page-by-slug': '/api/pages/lookup-by-slug/{slug}/',
        'page-by-tag': '/api/pages/lookup-by-tag/{slug}/',
        'page-by-path': '/api/pages/lookup-by-path/{site_id}/{path}',
        'pages-by-type': '/api/pages/'
    }

    version = pkg_resources.get_distribution(__package__).version

    def __init__(
        self, base_url, api_key, sender_id, timeout, default_service_name,
    ):
        super().__init__(base_url, api_key, sender_id, timeout)
        self.default_service_name = default_service_name

    @fallback(cache=caches['cms_fallback'])
    def fallback_cache_get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    def get(self, *args, use_fallback_cache=False, **kwargs):
        if use_fallback_cache:
            return self.fallback_cache_get(*args, **kwargs)
        return super().get(*args, **kwargs)

    def ping(self):
        return self.get(url=self.endpoints['ping'])

    def lookup_by_tag(
        self,
        slug,
        fields=None,
        draft_token=None,
        language_code=None,
        service_name=None,
    ):
        base_params = build_params(
            fields=fields, language_code=language_code, draft_token=draft_token
        )
        return self.get(
            url=self.endpoints['page-by-tag'].format(slug=slug),
            params={
                **base_params,
                'service_name': service_name or self.default_service_name,
            },
            use_fallback_cache=True,
        )

    def lookup_by_slug(
        self,
        slug,
        fields=None,
        draft_token=None,
        language_code=None,
        service_name=None,
        region=None,
    ):
        base_params = build_params(
            fields=fields, language_code=language_code,
            draft_token=draft_token, region=region
        )

        return self.get(
            url=self.endpoints['page-by-slug'].format(slug=slug),
            params={
                **base_params,
                'service_name': service_name or self.default_service_name,
            },
            use_fallback_cache=True,
        )

    def lookup_by_path(
        self,
        site_id,
        path,
        fields=None,
        draft_token=None,
        language_code=None,
        region=None,
    ):
        base_params = build_params(
            fields=fields,
            draft_token=draft_token,
            language_code=language_code,
            region=region,
        )
        url = self.endpoints['page-by-path'].format(site_id=site_id, path=path)
        return self.get(url=url, params=base_params, use_fallback_cache=True)

    def list_by_page_type(
        self,
        page_type,
        fields=None,
        draft_token=None,
        language_code=None,
        limit=None,
        offset=None
    ):
        base_params = build_params(
            fields=fields, language_code=language_code,
            draft_token=draft_token,
            limit=limit,
            offset=offset
        )
        return self.get(
            url=self.endpoints['pages-by-type'],
            params={
                **base_params,
                'type': page_type,
            },
            use_fallback_cache=True,
        )


cms_api_client = DirectoryCMSClient(
    base_url=settings.DIRECTORY_CMS_API_CLIENT_BASE_URL,
    api_key=settings.DIRECTORY_CMS_API_CLIENT_API_KEY,
    sender_id=settings.DIRECTORY_CMS_API_CLIENT_SENDER_ID,
    timeout=settings.DIRECTORY_CMS_API_CLIENT_DEFAULT_TIMEOUT,
    default_service_name=settings.DIRECTORY_CMS_API_CLIENT_SERVICE_NAME,
)

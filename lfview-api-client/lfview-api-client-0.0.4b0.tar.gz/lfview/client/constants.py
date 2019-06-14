"""Constants required for traversing the LF View API"""
from lfview.resources.files import FILES_REGISTRY
from lfview.resources.manifests import MANIFEST_REGISTRY
from lfview.resources.scene import SCENE_REGISTRY
from lfview.resources.spatial import SPATIAL_REGISTRY

# Upload chunk size must be a multiple of 256 KB
# A default of 20 MB works well for most connections
CHUNK_SIZE = 80 * 256 * 1024
IGNORED_PROPS = [
    'uid',
    'author',
]
RESOURCE_REGISTRIES = [
    FILES_REGISTRY,
    MANIFEST_REGISTRY,
    SCENE_REGISTRY,
    SPATIAL_REGISTRY,
]

DEFAUlT_URL_BASE = 'https://lfview.com'

DEFAULT_API_URL_SPEC = '{base}/api/v1'

USER_URL_SPEC = '{}/user'.format(DEFAULT_API_URL_SPEC)
ORG_URL_SPEC = '{}/orgs'.format(DEFAULT_API_URL_SPEC)
ORG_UID_URL_SPEC = ORG_URL_SPEC + '/{org}'
PROJECT_URL_SPEC = ORG_UID_URL_SPEC + '/projects'
PROJECT_UID_URL_SPEC = (
    '{}/project'.format(DEFAULT_API_URL_SPEC) + '/{org}/{project}'
)
PROJECT_UPLOAD_URL_SPEC = PROJECT_UID_URL_SPEC + '/{base_type}{sub_type}'
VIEW_INVITES_URL_SPEC = '{view_url}/invites'
VIEW_SLIDES_URL_SPEC = '{view_url}/slides'

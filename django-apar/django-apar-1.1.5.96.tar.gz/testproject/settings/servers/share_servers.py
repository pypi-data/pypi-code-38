from ..base import *

DEBUG = os.environ.get('DJANGO_DEBUG', "False") == "True"
# Application definition
INSTALLED_APPS += (
    #third party apps
    's3direct',
    #my apps
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

# Update database configuration with $DATABASE_URL.
if os.environ.get('HEROKU_ACTIVE', "False") == "False":
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ.get('DATABASE_NAME'),
            'USER': os.environ.get('DATABASE_USER'),
            'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
            'HOST': 'localhost',
            'PORT': '',
        }
    }

db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)
# Honor the 'X-Forwarded-Proto' header for request.is_secure()
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Amazon
AWS_HEADERS = {  # see http://developer.yahoo.com/performance/rules.html#expires
        'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
        'Cache-Control': 'max-age=94608000',
}

AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

if not AWS_SECRET_ACCESS_KEY or not AWS_ACCESS_KEY_ID or not AWS_STORAGE_BUCKET_NAME:
        raise ValueError('AWS KEY does not set')

S3DIRECT_REGION = os.environ.get('S3DIRECT_REGION', 'us-east-1')

if AWS_ACTIVE:
    # Tell django-storages that when coming up with the URL for an item in S3 storage, keep
    # it simple - just use this domain plus the path. (If this isn't set, things get complicated).
    # This controls how the `static` template tag from `staticfiles` gets expanded, if you're using it.
    # We also use it in the next setting.
    # AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
    AWS_S3_CUSTOM_DOMAIN = 's3-%s.amazonaws.com/%s' % (S3DIRECT_REGION, AWS_STORAGE_BUCKET_NAME)
    # This is used by the `static` template tag from `static`, if you're using that. Or if anything else
    # refers directly to STATIC_URL. So it's safest to always set it.
    # #
    STATICFILES_LOCATION = 'static'
    STATICFILES_STORAGE = 'custom_storages.StaticStorage'
    STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, STATICFILES_LOCATION)
    # #
    # STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    # STATIC_URL = '/static/'

    # MEDIA
    MEDIAFILES_LOCATION = 'media'
    MEDIA_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, MEDIAFILES_LOCATION)
    DEFAULT_FILE_STORAGE = 'custom_storages.MediaStorage'
else:
    MEDIA_URL = "/media/"
    MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "media")

    STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')
    STATIC_URL = '/static/'


def create_filename(filename):
    import uuid
    ext = filename.split('.')[-1]
    filename = '%s.%s' % (uuid.uuid4().hex, ext)
    return os.path.join('files', filename)

def create_file_filename(filename):
    import uuid
    ext = filename.split('.')[-1]
    filename = '%s.%s' % (uuid.uuid4().hex, ext)
    return os.path.join('file', filename)


S3DIRECT_DESTINATIONS = {
    # Allow anybody to upload any MIME type
    # 'misc': {
    #     'key': '/'
    # },

    # Allow staff users to upload any MIME type
    # 'pdfs': {
    #     'key': 'uploads/pdfs',
    #     'auth': lambda u: u.is_staff
    # },

    # Allow anybody to upload jpeg's and png's. Limit sizes to 500b - 4mb
    'images': {
        # 'key': 'uploads/images',
        'key': create_filename,
        'auth': lambda u: u.is_authenticated,
        'allowed': [
            'image/jpeg',
            'image/png'
        ],
        'content_length_range': (500, 4000000),
    },

    # Allow authenticated users to upload mp4's
    'videos': {
        # 'key': 'uploads/videos',
        'key': create_filename,
        'auth': lambda u: u.is_authenticated,
        'allowed': ['video/mp4']
    },

    'file': {
        # 'key': 'uploads/videos',
        'key': create_file_filename,
        'auth': lambda u: u.is_authenticated,
        # TODO: add mime type
        # 'allowed': ['application/octet-stream ipa']
    },
    # Allow anybody to upload any MIME type with a custom name function
    # 'custom_filename': {
    #     'key': create_filename
    # },
}
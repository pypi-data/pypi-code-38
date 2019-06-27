from .servers.share_servers import *
# from base import *
# #
DEBUG = True
#
# # INSTALLED_APPS += (
# #     #third party apps
# #         's3direct',
# #     #my apps
# # )
#
# #
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "media")

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, "static"),
# ]
STATIC_URL = '/static/'
#
# USE_TZ = True


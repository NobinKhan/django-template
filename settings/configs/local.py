from settings.configs.base import *


# Security settings
DEBUG = True
ALLOWED_HOSTS = ['*']


# media files config
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


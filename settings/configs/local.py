from settings.configs.base import *  # noqa: F403
from settings.configs.env import BASE_DIR

# installed apps and middleware
INSTALLED_APPS.append(  # noqa: F405
    "debug_toolbar",
)
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405
MIDDLEWARE.append(  # noqa: F405
    "debug_toolbar.middleware.DebugToolbarMiddleware",
)

INTERNAL_IPS = [
    "127.0.0.1",
]

# Security settings
DEBUG = True
ALLOWED_HOSTS = ["*"]


# media files config
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")  # noqa: F405

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")  # noqa: F405
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

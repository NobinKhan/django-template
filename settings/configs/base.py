import os

from settings.configs.env import env

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")


# Application definition (base)
INSTALLED_APPS = [
    # default apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # essential apps
    "corsheaders",
    "rest_framework",
    "drf_spectacular",
]


# Middleware definition
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# Template definition
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# Database Settings
DATABASES = {"default": env.db_url()}
DATABASES["default"]["ATOMIC_REQUESTS"] = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# redis cache
CACHE_TTL = 60 * 1500
CACHES = {
    "default": env.cache_url(),
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# URL & Server Definition
ROOT_URLCONF = "routes.urls"
WSGI_APPLICATION = "settings.servers.wsgi.application"
APPEND_SLASH = False


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Import Other Settings
from settings.modules.cors import *             # noqa: E402, F403
from settings.modules.sessions import *         # noqa: E402, F403
from settings.modules.token import *            # noqa: E402, F403

if "rest_framework" in INSTALLED_APPS:
    from settings.modules.drf import *          # noqa: E402, F403
    from settings.modules.rest_docs import *    # noqa: E402, F403

import os

from django.core.wsgi import get_wsgi_application

from settings.configs.env import * # noqa: F403

os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"settings.configs.{ENVIRONMENT}")  # noqa: F405

application = get_wsgi_application()

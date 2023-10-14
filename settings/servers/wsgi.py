import os
from settings.configs.env import *


from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', f"settings.configs.{ENVIRONMENT}")

application = get_wsgi_application()

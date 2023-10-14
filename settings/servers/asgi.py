import environ
import os
from pathlib import Path


# Set the project Environment
ENVIRONMENT = os.environ.get('DJANGO_ENVIRONMENT')
if not ENVIRONMENT:
    raise ImportError({"Django": "Emproperly Configured System."})

# Set the project base directory
BASE_DIR = os.environ.get('DJANGO_BASE_DIR')
if not BASE_DIR:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    # Take environment variables from .env file
    environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', f"settings.configs.{ENVIRONMENT}")

application = get_asgi_application()

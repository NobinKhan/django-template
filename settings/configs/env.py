import os
import environ
from pathlib import Path


env = environ.Env()

# Set the project base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Set the project Environment
ENVIRONMENT = os.environ.get('DJANGO_ENVIRONMENT')
if not ENVIRONMENT:
    raise ImportError({"Django": "Emproperly Configured System."})


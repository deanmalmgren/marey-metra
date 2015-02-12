import os
import sys

# Add the app code to the path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

os.environ['CELERY_LOADER'] = 'django'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

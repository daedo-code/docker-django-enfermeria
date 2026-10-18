import sys, os

# Ruta de tu proyecto
project_home = '/home/usuario/misitio'
if project_home not in sys.path:
    sys.path.append(project_home)

os.environ['DJANGO_SETTINGS_MODULE'] = 'miproyecto.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
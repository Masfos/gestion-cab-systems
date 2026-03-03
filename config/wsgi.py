import os
from django.core.wsgi import get_wsgi_application

# Configuración WSGI para producción
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()
import os
from django.core.asgi import get_asgi_application

# Configuración ASGI para posibles implementaciones de Channels
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_asgi_application()
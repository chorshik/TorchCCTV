"""
ASGI config for web_app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os
import web_app.urls

from channels.http import AsgiHandler
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter,URLRouter

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_app.settings')

application = ProtocolTypeRouter({
    # handle http
    "http": get_asgi_application(),

    # handle ws/wss
    'websocket': AuthMiddlewareStack(URLRouter(web_app.urls.websocket_urlpatterns))

})

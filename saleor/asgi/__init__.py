"""ASGI config for Saleor project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from saleor.asgi.health_check import health_check
#import channels
import django
django.setup()
from saleor.graphql.api import MyGraphqlWsConsumer
#import django
#django.setup()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saleor.settings")
#django.setup()

application1 = get_asgi_application()
from channels.auth import AuthMiddlewareStack
from channels.routing import URLRouter, ProtocolTypeRouter
application1 = health_check(application1, "/health/")
#application.setup()
application = ProtocolTypeRouter(
    {
        "http": application1,
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [django.urls.path("graphql/", MyGraphqlWsConsumer.as_asgi())]
            )
        ),
    }
)


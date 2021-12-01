"""ASGI config for Saleor project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
import channels
from saleor.asgi.health_check import health_check

import channels_graphql_ws

print("TESTTT")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saleor.settings")

# class MyGraphqlWsConsumer(channels_graphql_ws.GraphqlWsConsumer):
#     """Channels WebSocket consumer which provides GraphQL API."""

#     async def on_connect(self, payload):
#         """Handle WebSocket connection event."""

#         # Use auxiliary Channels function `get_user` to replace an
#         # instance of `channels.auth.UserLazyObject` with a native
#         # Django user object (user model instance or `AnonymousUser`)
#         # It is not necessary, but it helps to keep resolver code
#         # simpler. Cause in both HTTP/WebSocket requests they can use
#         # `info.context.user`, but not a wrapper. For example objects of
#         # type Graphene Django type `DjangoObjectType` does not accept
#         # `channels.auth.UserLazyObject` instances.
        # https://github.com/datadvance/DjangoChannelsGraphqlWs/issues/23
        # self.scope["user"] = await channels.auth.get_user(self.scope)

application = get_asgi_application()
application = health_check(application, "/health/")

from channels.routing import ProtocolTypeRouter, URLRouter
from .graphql.notifications.sockets import MyGraphqlWsConsumer
from django.urls import path
from django.conf.urls import url
from channels.staticfiles import StaticFilesHandler
from django.core.asgi import get_asgi_application
import channels
from django.urls import re_path
from channels.auth import AuthMiddlewareStack
import django
# websocket_urlPattern = [
#     path("", MyGraphqlWsConsumer.as_asgi()),
# ]
# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(
#         URLRouter(websocket_urlPattern)
#     ),
# })
print("==application==")
application = channels.routing.ProtocolTypeRouter(
    {
        "http": django.core.asgi.get_asgi_application(),
        "websocket": channels.auth.AuthMiddlewareStack(
            channels.routing.URLRouter(
                [django.urls.path("graphql/", MyGraphqlWsConsumer.as_asgi())]
            )
        ),
    }
)

channel_routing = {
    'http.request': StaticFilesHandler()
}

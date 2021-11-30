"""WSGI config for Saleor project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.
"""
import eventlet.wsgi
import eventlet
from saleor.views import background_thread, sio
from django.contrib.staticfiles.handlers import StaticFilesHandler
import socketio
import os

from django.core.wsgi import get_wsgi_application
from django.utils.functional import SimpleLazyObject
import logging
from saleor.wsgi.health_check import health_check


def get_allowed_host_lazy():
    from django.conf import settings

    return settings.ALLOWED_HOSTS[0]


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saleor.settings")

#application = get_wsgi_application()
#application = health_check(application, "/health/")

# Warm-up the django application instead of letting it lazy-load
#application(
#     {
#         "REQUEST_METHOD": "GET",
#         "SERVER_NAME": SimpleLazyObject(get_allowed_host_lazy),
#         "REMOTE_ADDR": "127.0.0.1",
#         "SERVER_PORT": 80,
#         "PATH_INFO": "/graphql/",
#         "wsgi.input": b"",
#         "wsgi.multiprocess": True,
#     },
#     lambda x, y: None,
# )

# import socketio
# from django.http import HttpResponse

# sio = socketio.Server(async_mode=None)
# thread = None

# def background_thread():
#     """Example of how to send server generated events to clients."""
#     count = 0
#     while True:
#         sio.sleep(10)
#         count += 1
#         sio.emit('my_response', {'data': 'Server generated event'},
#                  namespace='/test')

# def index(request):
#     global thread
#     if thread is None:
#         thread = sio.start_background_task(background_thread)
#     return HttpResponse("====TEST===")
# # create a Socket.IO server
# # sio = socketio.Server(async_mode=None)
# # sio.emit('my event', {'data': 'foobar'})
# # wrap with ASGI application

# @sio.on('connect')
# def connect(sid, message):
#     print("connected")
#     sio.emit('my_response', {'data': 'Connected', 'count': 0}, room=sid)


# import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saleor.settings")
django_app = StaticFilesHandler(get_wsgi_application())
application = socketio.WSGIApp(sio, django_app)

import eventlet
import eventlet.wsgi
print("==TEST==")

thread = sio.start_background_task(background_thread)
eventlet.wsgi.server(eventlet.listen(('', 8080)), application)




from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
import json
import os
from saleor.core.jwt import get_domain_from_request

from saleor.store.models import Store

from .manager import get_plugins_manager


def handle_plugin_webhook(request: WSGIRequest, plugin_id: str) -> HttpResponse:
    manager = get_plugins_manager()
    return manager.webhook_endpoint_without_channel(request, plugin_id)


def handle_global_plugin_webhook(request: WSGIRequest, plugin_id: str) -> HttpResponse:
    manager = get_plugins_manager()
    return manager.webhook(request, plugin_id, channel_slug=None)


def handle_plugin_per_channel_webhook(
    request: WSGIRequest, plugin_id: str, channel_slug: str
) -> HttpResponse:
    manager = get_plugins_manager()
    return manager.webhook(request, plugin_id, channel_slug=channel_slug)

def handle_manifest(request: WSGIRequest) -> HttpResponse:
    domain = get_domain_from_request(request)
    path = os.path.join(
        settings.PROJECT_ROOT, "saleor", "static", "manifest.json"
    )
    with open(path) as f:
        manifest = json.load(f)
        if manifest:
            store = Store.objects.filter(domain=domain).first()
            if store:
                manifest["name"] = store.name
                if store.favicon:
                    icon = {
                    "src": str(store.favicon),
                    "type": "image/png",
                    "sizes": "512x512"
                    }
                    manifest["icons"].append(icon)
    return HttpResponse(json.dumps(manifest), content_type="application/json")



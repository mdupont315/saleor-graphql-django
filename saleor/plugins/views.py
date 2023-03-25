from django.conf import settings
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django_multitenant.utils import get_current_tenant
from saleor.core.utils.logging import log_info
import json
import os
from saleor.core.jwt import get_domain_from_request

from saleor.store.models import Store,FaviconPwa

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
    # domain = get_domain_from_request(request)
    path = os.path.join(
        settings.PROJECT_ROOT, "saleor", "static", "manifest.json"
    )
    with open(path) as f:
        manifest = json.load(f)
        if manifest:
            store = get_current_tenant()
            if store:
                store_favicon_pwa = FaviconPwa.objects.filter(store_id=store.id)
                manifest["name"] = store.name
                manifest["short_name"] = store.name
                manifest["start_url"] = "https://" + store.domain 
                if store_favicon_pwa:
                    for favicon in store_favicon_pwa:
                        icon = {
                        "src": settings.STATIC_URL + str(favicon.image),
                        "type": favicon.type,
                        "sizes": str(favicon.size) + "x" + str(favicon.size)
                        }
                        manifest["icons"].append(icon)
    return HttpResponse(json.dumps(manifest), content_type="application/json")



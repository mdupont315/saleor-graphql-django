import logging
from datetime import datetime

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import MiddlewareNotUsed
from django.utils import timezone
from django.utils.functional import SimpleLazyObject
from django.utils.translation import get_language

from saleor.store import models
from django_multitenant.utils import set_current_tenant, unset_current_tenant

from ..discount.utils import fetch_discounts
from ..plugins.manager import get_plugins_manager
from . import analytics
from .jwt import JWT_REFRESH_TOKEN_COOKIE_NAME, get_domain_from_request, jwt_decode_with_exception_handler

logger = logging.getLogger(__name__)


def google_analytics(get_response):
    """Report a page view to Google Analytics."""

    if not settings.GOOGLE_ANALYTICS_TRACKING_ID:
        raise MiddlewareNotUsed()

    def _google_analytics_middleware(request):
        client_id = analytics.get_client_id(request)
        path = request.path
        language = get_language()
        headers = request.META
        try:
            analytics.report_view(
                client_id, path=path, language=language, headers=headers
            )
        except Exception:
            logger.exception("Unable to update analytics")
        return get_response(request)

    return _google_analytics_middleware


def request_time(get_response):
    def _stamp_request(request):
        request.request_time = timezone.now()
        return get_response(request)

    return _stamp_request

def request_set_tenant(get_response):
    def _request_set_tenant(request):
        domain = get_domain_from_request(request)
        if domain:
            unset_current_tenant()
            # check if this domain is custom domain? 
            custom_domain = models.CustomDomain.objects.filter(domain_custom = domain, status = True).first()
            s_domain = models.Store.objects.filter(domain=domain).first()

            # if enable_custom_domain:
            if s_domain:
                set_current_tenant(s_domain)
            elif custom_domain:
                 # find store by custom domain ----------------
                s_custom_domain = models.Store.objects.filter(id=custom_domain.store_id,custom_domain_enable=True).first()
                if s_custom_domain:
                    set_current_tenant(s_custom_domain)
        return get_response(request)

    return _request_set_tenant

def discounts(get_response):
    """Assign active discounts to `request.discounts`."""

    def _discounts_middleware(request):
        request.discounts = SimpleLazyObject(
            lambda: fetch_discounts(request.request_time)
        )
        return get_response(request)

    return _discounts_middleware


def site(get_response):
    """Clear the Sites cache and assign the current site to `request.site`.

    By default django.contrib.sites caches Site instances at the module
    level. This leads to problems when updating Site instances, as it's
    required to restart all application servers in order to invalidate
    the cache. Using this middleware solves this problem.
    """

    def _get_site():
        Site.objects.clear_cache()
        return Site.objects.get_current()

    def _site_middleware(request):
        request.site = SimpleLazyObject(_get_site)
        return get_response(request)

    return _site_middleware


def plugins(get_response):
    """Assign plugins manager."""

    def _get_manager():
        return get_plugins_manager()

    def _plugins_middleware(request):
        request.plugins = SimpleLazyObject(lambda: _get_manager())
        return get_response(request)

    return _plugins_middleware


def jwt_refresh_token_middleware(get_response):
    def middleware(request):
        """Append generated refresh_token to response object."""
        response = get_response(request)
        jwt_refresh_token = getattr(request, "refresh_token", None)
        if jwt_refresh_token:
            expires = None
            if settings.JWT_EXPIRE:
                refresh_token_payload = jwt_decode_with_exception_handler(
                    jwt_refresh_token
                )
                if refresh_token_payload and refresh_token_payload.get("exp"):
                    expires = datetime.utcfromtimestamp(
                        refresh_token_payload.get("exp")
                    )
            response.set_cookie(
                JWT_REFRESH_TOKEN_COOKIE_NAME,
                jwt_refresh_token,
                expires=expires,
                httponly=True,  # protects token from leaking
                secure=not settings.DEBUG,
            )
        return response

    return middleware

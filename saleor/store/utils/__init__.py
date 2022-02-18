from typing import TYPE_CHECKING, Dict, Iterable, List, Union

from django.conf import settings
from django.db import transaction
from ..models import Store
import dns.resolver
import requests
import json


if TYPE_CHECKING:
    # flake8: noqa
    from datetime import date, datetime

    from django.db.models.query import QuerySet

    from ...order.models import Order, OrderLine
    from ..models import Store


@transaction.atomic
def delete_stores(stores_ids: List[str]):
    """Delete stores and perform all necessary actions.

    Set products of deleted stores as unpublished.
    """
    stores = Store.objects.select_for_update().filter(pk__in=stores_ids)
    stores.delete()

def check_dns(domain):
    try:
        result = dns.resolver.query(domain, 'A')
        if result:
            return True
        else: 
            return False
    except:
        return False

# import requests

def verify_ssl(domain):
 
    # Making a get request
    # response = requests.get('https://{}'.format(domain), verify = False)
 # Making a get request
    api_url = settings.VERIFY_SSL_API
    pay_load = {"domain": domain}
    response = requests.post(api_url, pay_load)
    response = json.loads(response._content.decode("utf-8"))['error']
    return response
 
# # print request object
#     # print request object
#     print(response)

# verify_ssl('orderich.site')
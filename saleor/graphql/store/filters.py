import django_filters

from saleor.graphql.core.filters import MetadataFilterBase
from ...store import models
from ..utils.filters import filter_by_query_param, filter_fields_containing_value, filter_range_field
from ..core.types import FilterInputObjectType

def filter_store_type(qs, _, value):
    return filter_range_field(qs, "store_type", value)


def filter_search(qs, _, value):
    search_fields = ("name",)
    if value:
        qs = filter_by_query_param(qs, value, search_fields)
    return qs


class StoreFilter(django_filters.FilterSet):
    store_type =  django_filters.CharFilter(method=filter_store_type)    
    search = django_filters.CharFilter(method=filter_search)

    class Meta:
        model = models.Store
        fields = [
            "store_type",            
            "search",
        ]

class StoreFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = StoreFilter

class CustomDomainFilter(MetadataFilterBase):
    search = django_filters.CharFilter(
        method=filter_fields_containing_value("table_name")
    )

    class Meta:
        model = models.CustomDomain
        fields = ["domain_custom"]


class CustomDomainFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = CustomDomainFilter

class FaviconPwaFilter(MetadataFilterBase):
    search = django_filters.CharFilter(
        method=filter_fields_containing_value("table_name")
    )

    class Meta:
        model = models.FaviconPwa
        fields = ["size"]


class FaviconPwaFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = FaviconPwaFilter
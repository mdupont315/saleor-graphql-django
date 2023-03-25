
import django_filters
import graphene
from ..core.filters import (
    MetadataFilterBase,
)
from ..utils.filters import filter_fields_containing_value
from saleor.graphql.core.types.filter_input import FilterInputObjectType
from ...table_service.models import TableService


class TableServiceFilter(MetadataFilterBase):
    search = django_filters.CharFilter(
        method=filter_fields_containing_value("table_name")
    )

    class Meta:
        model = TableService
        fields = ["table_name"]


class TableServiceFilterInput(FilterInputObjectType):
    class Meta:
        filterset_class = TableServiceFilter
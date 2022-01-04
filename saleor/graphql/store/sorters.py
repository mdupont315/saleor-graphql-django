import graphene
from django.db.models import Count, QuerySet
from ..core.types import SortInputObjectType


class StoreSortField(graphene.Enum):
    NAME = ["name", "pk"]
    DESCRIPTION = ["description", "pk"]
    
    @property
    def description(self):
        if self.name in StoreSortField.__enum__._member_names_:
            sort_name = self.name.lower().replace("_", " ")
            return f"Sort users by {sort_name}."
        raise ValueError("Unsupported enum value: %s" % self.value)

    @staticmethod
    def qs_with_order_count(queryset: QuerySet, **_kwargs) -> QuerySet:
        return queryset.annotate(order_count=Count("orders__id"))


class StoreSortingInput(SortInputObjectType):
    class Meta:
        sort_enum = StoreSortField
        type_name = "stores"

class CustomDomainSortField(graphene.Enum):
    NAME = ["domain_custom", "id"]

    @property
    def description(self):
        # pylint: disable=no-member
        descriptions = {
            CustomDomainSortInput.NAME.name: "domain_custom",
        }
        if self.name in descriptions:
            return f"Sort table services by {descriptions[self.name]}."
        raise ValueError("Unsupported enum value: %s" % self.value)


class CustomDomainSortInput(SortInputObjectType):
    class Meta:
        sort_enum = CustomDomainSortField
        type_name = "custom domain types"

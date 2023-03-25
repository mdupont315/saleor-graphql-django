

from saleor.graphql.core.types.sort_input import SortInputObjectType
import graphene


class TableServiceSortField(graphene.Enum):
    NAME = ["table_name", "id"]

    @property
    def description(self):
        # pylint: disable=no-member
        descriptions = {
            TableServiceSortField.NAME.name: "table_name",
        }
        if self.name in descriptions:
            return f"Sort table services by {descriptions[self.name]}."
        raise ValueError("Unsupported enum value: %s" % self.value)


class TableServiceSortInput(SortInputObjectType):
    class Meta:
        sort_enum = TableServiceSortField
        type_name = "table service types"

import graphene

from ...core.tracing import traced_resolver
from ..core.utils import from_global_id_or_error
from ..decorators import staff_member_or_app_required
from .mutations import (
    ChannelActivate,
    ChannelCreate,
    ChannelDeactivate,
    ChannelDelete,
    ChannelUpdate,
)
from .resolvers import resolve_channel, resolve_channels, resolve_channel_by_slug
from .types import Channel


class ChannelQueries(graphene.ObjectType):
    channel = graphene.Field(
        Channel,
        id=graphene.Argument(graphene.ID, description="ID of the channel."),
        description="Look up a channel by ID.",
    )
    channels = graphene.List(
        graphene.NonNull(Channel), description="List of all channels."
    )
    channel_by_slug = graphene.Field(
        Channel,
        slug=graphene.Argument(graphene.String, description="Slug of the channel."),
        description="Look up a channel by ID.",
    )

    @staff_member_or_app_required
    def resolve_channel(self, info, id=None, **kwargs):
        _, id = from_global_id_or_error(id, Channel)
        return resolve_channel(id)

    @staff_member_or_app_required
    @traced_resolver
    def resolve_channels(self, _info, **kwargs):
        return resolve_channels()

    def resolve_channel_by_slug(self, info, slug=None, **kwargs):
        return resolve_channel_by_slug(slug)

class ChannelMutations(graphene.ObjectType):
    channel_create = ChannelCreate.Field()
    channel_update = ChannelUpdate.Field()
    channel_delete = ChannelDelete.Field()
    channel_activate = ChannelActivate.Field()
    channel_deactivate = ChannelDeactivate.Field()

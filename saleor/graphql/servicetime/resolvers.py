import graphene
from saleor.graphql.notifications.schema import LiveNotification
from ...servicetime import models


def resolve_service_time(self, info, **kwargs):
    LiveNotification(message_id="id", message_title="title")
    return models.ServiceTime.objects.all()

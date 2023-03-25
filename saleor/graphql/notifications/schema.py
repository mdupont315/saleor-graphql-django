import channels_graphql_ws
import graphene

# from django.contrib.auth import get_user_model

# from graphql_api.core.utils import from_global_id

# USER = get_user_model()


class LiveNotification(channels_graphql_ws.Subscription):
    store_id = graphene.String()
    message_title = graphene.String()

    class Arguments:
        id = graphene.ID(required=True)

    # @staticmethod
    # def subscribe(root, info, *args, **kwds):
    #     _, current_user_id = from_global_id(kwds.get('id'))
    #     user_id = [current_user_id] if USER.objects.get(pk=current_user_id) else None
    #     return user_id
    def subscribe(self, info, id=None):
        """Client subscription handler."""
        del info
        # Specify the subscription group client subscribes to.
        return [id] if id is not None else None

    def publish(self, info, **arg1):
        store_id = self["store_id"]
        message_title = self["message_title"]
        return LiveNotification(store_id=store_id, message_title=message_title)

    @classmethod
    def new_message(cls, store_id, message_title):
        """Auxiliary function to send subscription notifications.

        It is generally a good idea to encapsulate broadcast invocation
        inside auxiliary class methods inside the subscription class.
        That allows to consider a structure of the `payload` as an
        implementation details.
        """
        cls.broadcast(
            group=store_id,
            payload={"store_id": store_id, "message_title": message_title},
        )

class AppNotification(graphene.ObjectType):
    app_live_notification = LiveNotification.Field()

# schema = graphene.Schema(subscription=AppNotification)
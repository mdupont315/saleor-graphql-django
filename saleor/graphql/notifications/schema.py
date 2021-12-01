import channels_graphql_ws
import graphene

# from django.contrib.auth import get_user_model

# from graphql_api.core.utils import from_global_id

# USER = get_user_model()


class LiveNotification(channels_graphql_ws.Subscription):
    message_id = graphene.String()
    message_title = graphene.String()

    class Arguments:
        id = graphene.ID(required=True)

    # @staticmethod
    # def subscribe(root, info, *args, **kwds):
    #     _, current_user_id = from_global_id(kwds.get('id'))
    #     user_id = [current_user_id] if USER.objects.get(pk=current_user_id) else None
    #     return user_id

    @staticmethod
    def publish(payload, info, **arg1):
        id = payload["id"]
        title = payload["title"]
        return LiveNotification(message_id=id, message_title=title)


class AppNotification(graphene.ObjectType):
    app_live_notification = LiveNotification.Field()

schema = graphene.Schema(subscription=AppNotification)
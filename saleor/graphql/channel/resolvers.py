from ...channel import models


def resolve_channel(id):
    return models.Channel.objects.filter(id=id).first()


def resolve_channels():
    return models.Channel.objects.all()

def resolve_channel_by_slug(slug):
    return models.Channel.objects.filter(slug=slug).first()
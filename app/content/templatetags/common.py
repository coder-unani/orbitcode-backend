from django import template
from config.settings.settings import URL_THUMBNAIL

register = template.Library()


@register.filter
def url_thumbnail(value):
    return URL_THUMBNAIL + value

from django import template

from config.settings.settings import THUMBNAIL_BASE_URL

register = template.Library()


@register.filter(name='add_base_url')
def add_base_url(url):
    base_url = THUMBNAIL_BASE_URL
    return f"{base_url}{url}"


@register.filter(name='truncatechars')
def truncatechars(value, arg):
    try:
        length = int(arg)
    except ValueError:
        return value  # Invalid argument, return the original text

    if len(value) > length:
        return value[:length] + '...'
    return value
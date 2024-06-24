from django import template

from config.settings.settings import AWS_S3_BASE_URL

register = template.Library()


@register.filter(name='add_base_url')
def add_base_url(url):
    base_url = AWS_S3_BASE_URL
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


@register.filter(name='default_people_image')
def default_people_image(value):
    base_url = AWS_S3_BASE_URL
    if not value:
        return '/static/images/no-people.png'
    return f"{base_url}{value}"

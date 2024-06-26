from django import template

from config.settings.settings import AWS_S3_BASE_URL

register = template.Library()


@register.filter(name='add_base_url')
def add_base_url(url):
    if not url:
        return url
    return f"{AWS_S3_BASE_URL}{url}"


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


@register.filter
def file_size_format(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "N/A"
    if value < 1024:
        return f"{value} B"
    elif value < 1024 ** 2:
        return f"{value / 1024:.2f} KB"
    elif value < 1024 ** 3:
        return f"{value / 1024 ** 2:.2f} MB"
    elif value < 1024 ** 4:
        return f"{value / 1024 ** 3:.2f} GB"
    else:
        return f"{value / 1024 ** 4:.2f} TB"

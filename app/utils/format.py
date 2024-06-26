from datetime import datetime


def format_datetime_to_str(dt, date_format='%Y-%m-%d %H:%M:%S'):
    if isinstance(dt, datetime):
        raise ValueError('Invalid datetime format')
    return dt.strftime(date_format)


from django import template
from datetime import timedelta

register = template.Library()


@register.filter
def format_duration(td):
    if not isinstance(td, timedelta):
        return "00:00:00"  # Return a default string if not a timedelta

    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f'{hours:02}:{minutes:02}'

from django import template

register = template.Library()

@register.filter
def times(number):
    """Return a range up to number for looping in templates. Treat None as 0."""
    if not number:
        return range(0)
    return range(number)

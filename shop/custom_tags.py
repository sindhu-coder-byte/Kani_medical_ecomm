from django import template

register = template.Library()

@register.filter
def times(number):
    """Return a range up to number for looping in templates."""
    return range(number)

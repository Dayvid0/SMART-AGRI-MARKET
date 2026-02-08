from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """
    Multiply the value by the arg
    Usage: {{ value|mul:20 }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
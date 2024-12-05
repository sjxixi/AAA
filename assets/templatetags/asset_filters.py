from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    """将值乘以参数"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0 
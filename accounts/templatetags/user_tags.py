from django import template

register = template.Library()

@register.filter
def can_edit_device(user, device):
    """
    模板过滤器：检查用户是否可以编辑设备
    用法: {% if user|can_edit_device:device %}
    """
    return user.can_edit_device(device) 
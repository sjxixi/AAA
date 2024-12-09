from django import template

register = template.Library()

@register.filter
def get_field(form, field_name):
    """获取表单字段"""
    return form[field_name]

@register.filter
def can_edit_server(user, server):
    """检查用户是否可以编辑服务器"""
    if user.is_admin:
        return True
    return user.has_perm('assets.change_server', server)

@register.filter
def can_edit_device(user, device):
    """检查用户是否可以编辑设备"""
    if user.is_admin:
        return True
    model_name = device._meta.model_name
    return user.has_perm(f'assets.change_{model_name}', device) 
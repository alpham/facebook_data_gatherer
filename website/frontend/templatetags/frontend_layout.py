from django import template

register = template.Library()

@register.inclusion_tag('_layout/head.html')
def layout_head():
    return {}

@register.inclusion_tag('_layout/scripts.html')
def load_scripts():
    return {}

#

# @register.inclusion_tag('base/frontend/layouts/layout_sidebar.html', takes_context=True)
# def layout_sidebar(context):
#     return {'user': context.get('user')}
#
# @register.inclusion_tag('base/frontend/layouts/layout_footer.html', takes_context=True)
# def layout_footer(context):
#     return {'user': context.get('user')}

from django import template

register = template.Library()


@register.inclusion_tag('_layout/head.html')
def layout_head():
    return {}


@register.inclusion_tag('_layout/footer.html')
def layout_footer():
    return {}


@register.inclusion_tag('_layout/scripts.html')
def load_scripts():
    return {}


@register.inclusion_tag('_layout/sections/home.html')
def section_home():
    return {}


@register.inclusion_tag('_layout/sections/contact.html')
def section_contact():
    return {}


@register.inclusion_tag('_layout/sections/about.html')
def section_about():
    return {}


@register.inclusion_tag('_layout/sections/pricing.html')
def section_pricing():
    return {}


@register.inclusion_tag('_layout/sections/feature_1.html')
def section_feature_1():
    return {}


@register.inclusion_tag('_layout/sections/feature.html')
def section_feature():
    return {}



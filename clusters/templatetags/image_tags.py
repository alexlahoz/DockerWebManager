from django import template

register = template.Library()

@register.filter
def get_image_name(tag):
    return tag.split(':')[0] if tag and ':' in tag else tag

@register.filter
def get_image_tag(tag):
    return tag.split(':')[1] if tag and ':' in tag else ''

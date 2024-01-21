from django import template

register=template.Library()

@register.filter(name='get_replies')
def get_dict(dict, key):
    return dict.get(key)
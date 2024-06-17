from django import template
from App.models import Comment,Post
register=template.Library()

@register.filter(name='get_replies')
def get_dict(dict, key):
    return dict.get(key)

@register.filter(name='get_comments')
def get_comments(post):
    return post.comment_set.filter(parent=None).count()
#     return post.comment_set.filter(parent=None)


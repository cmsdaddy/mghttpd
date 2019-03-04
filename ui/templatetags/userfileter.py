import datetime
from django import template
from django.template.base import (Node, NodeList, TemplateSyntaxError)

register = template.Library()


@register.filter(name='have')
def have(body, finger):
    if body.find(finger) < 0:
        return False
    return True


@register.filter(name='odd')
def odd(v):
    print(v, type(v))
    return True


@register.filter(name='zoom')
def zoom(v, dot):
    print(v, type(v))
    try:
        v = int(v)
    except:
        return ''

    try:
        fmt = "%%.%df" % dot
        val = fmt % (v / (10 ** dot))
        #print(v, dot, val)
        return val
    except:
        return '/'

from django import template
from website.models import Category


register = template.Library()


def getC():
    cats = Category.objects.only('name', 'slug')
    return cats
register.simple_tag(getC)


@register.filter(is_safe=True)
def good(value):
    return value

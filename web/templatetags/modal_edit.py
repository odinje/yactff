from django import template

register = template.Library()


@register.filter
def modal_edit(value, send_url):
    pass

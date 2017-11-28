from django import template

register = template.Library()

@register.simple_tag
def order_fish_quantity_tag(order, fish, *args, **kwargs):
    return order.fish

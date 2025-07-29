
# Dans votre fichier templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def has_image_extension(value):
    return value.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
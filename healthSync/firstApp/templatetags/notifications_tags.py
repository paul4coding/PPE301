from django import template
from firstApp.models import Notification

register = template.Library()

@register.simple_tag
def get_notifications():
    return Notification.objects.all().order_by('-date')
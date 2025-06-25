from django import template
from firstApp.models import Notification

register = template.Library()

@register.simple_tag(takes_context=True)
def get_notifications(context):
    user = context.get('user')
    # Détection du vrai profil objet
    if hasattr(user, 'patient'):
        user_obj = user.patient
    elif hasattr(user, 'medecin'):
        user_obj = user.medecin
    elif hasattr(user, 'secretaire'):
        user_obj = user.secretaire
    elif hasattr(user, 'laborantin'):
        user_obj = user.laborantin
    else:
        user_obj = user
    return Notification.objects.filter(destinataire=user_obj).order_by('-date')[:10]
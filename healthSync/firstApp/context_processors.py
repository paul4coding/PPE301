# ton_app/context_processors.py

from .models import Utilisateur
from .models import Notification

def utilisateur_connecte(request):
    user_id = request.session.get('user_id')
    if user_id:
        try:
            utilisateur = Utilisateur.objects.get(id=user_id)
            return {'utilisateur_connecte': utilisateur}
        except Utilisateur.DoesNotExist:
            pass
    return {}



def notifications_processor(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(destinataire=request.user).order_by('-date')[:10]
    else:
        notifications = []
    return {'notifications': notifications}

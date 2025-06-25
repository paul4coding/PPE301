# ton_app/context_processors.py

from .models import Utilisateur
from .models import Notification
from firstApp.models import Message

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
    notifications = []
    if request.user.is_authenticated:
        # Détection du vrai profil
        user_obj = None
        if hasattr(request.user, 'patient'):
            user_obj = request.user.patient
        elif hasattr(request.user, 'medecin'):
            user_obj = request.user.medecin
        elif hasattr(request.user, 'secretaire'):
            user_obj = request.user.secretaire
        elif hasattr(request.user, 'laborantin'):
            user_obj = request.user.laborantin
        else:
            user_obj = request.user
        notifications = Notification.objects.filter(destinataire=user_obj).order_by('-date')[:10]
    return {'notifications': notifications}


def notif_marquees_lues(request):
    return {
        'notif_marquees_lues': request.session.get('notifications_marquees_lues', False)
    }




def messages_non_lus(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {"messages_non_lus": [], "nb_messages_non_lus": 0}
    qs = Message.objects.filter(
        conversation__participants=user
    ).exclude(
        expediteur=user
    ).exclude(
        lu_par=user
    )
    messages = qs.order_by('-date_envoi')[:5]
    nb_messages_non_lus = qs.count()
    return {
        "messages_non_lus": messages,
        "nb_messages_non_lus": nb_messages_non_lus,
    }
    
    
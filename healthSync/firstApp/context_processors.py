# ton_app/context_processors.py

from .models import Utilisateur

def utilisateur_connecte(request):
    user_id = request.session.get('user_id')
    if user_id:
        try:
            utilisateur = Utilisateur.objects.get(id=user_id)
            return {'utilisateur_connecte': utilisateur}
        except Utilisateur.DoesNotExist:
            pass
    return {}

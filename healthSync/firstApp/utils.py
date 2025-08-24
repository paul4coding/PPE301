from django.core.mail import send_mail
from datetime import datetime

def envoyer_notification_rdv(rdv):
    # Combiner la date et l'heure
    date_heure = datetime.combine(rdv.date, rdv.heure)

    sujet = f"Confirmation de rendez-vous - {date_heure.strftime('%d/%m/%Y %H:%M')}"
    message = (
        f"Bonjour {rdv.patient.nom},\n\n"
        f"Votre rendez-vous avec le Dr. {rdv.medecin.nom} est bien enregistré "
        f"pour le {date_heure.strftime('%d/%m/%Y à %H:%M')}.\n\n"
        "Merci d'arriver 10 minutes en avance.\n\n"
        "Cordialement,\nL'équipe HealthSync"
    )

    send_mail(
        sujet,
        message,
        None,  # utilise DEFAULT_FROM_EMAIL
        [rdv.patient.email],
        fail_silently=False,
    )

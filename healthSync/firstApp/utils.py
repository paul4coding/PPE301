from django.core.mail import send_mail

def envoyer_notification_rdv(rdv):
    sujet = f"Confirmation de rendez-vous - {rdv.date.strftime('%d/%m/%Y %H:%M')}"
    message = (
        f"Bonjour {rdv.patient.nom},\n\n"
        f"Votre rendez-vous avec le Dr. {rdv.medecin.nom} est bien enregistré "
        f"pour le {rdv.date.strftime('%d/%m/%Y à %H:%M')}.\n\n"
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

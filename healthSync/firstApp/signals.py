from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RendezVous, Notification, Secretaire

@receiver(post_save, sender=RendezVous)
def notifie_creation_ou_modification_rdv(sender, instance, created, **kwargs):
    patient = instance.patient
    medecin = instance.medecin

    nom_medecin = f"{getattr(medecin, 'prenom', '')} {getattr(medecin, 'nom', '')}".strip()
    nom_patient = f"{getattr(patient, 'prenom', '')} {getattr(patient, 'nom', '')}".strip()
    statut = instance.get_statut_display() if hasattr(instance, 'get_statut_display') else instance.statut
    url = "#"  # Remplace par l'URL du détail du RDV si besoin

    if created:
        # Notification pour le patient
        Notification.objects.create(
            destinataire=patient,
            message=f"Votre rendez-vous avec le Dr {nom_medecin} a été planifié pour le {instance.date} à {instance.heure}.",
            lien=url,
            type="rendezvous"
        )

        # Notification pour le médecin
        Notification.objects.create(
            destinataire=medecin,
            message=f"Un nouveau rendez-vous a été planifié avec le patient {nom_patient} le {instance.date} à {instance.heure}.",
            lien=url,
            type="rendezvous"
        )

        # Notification pour tous les secrétaires
        for sec in Secretaire.objects.all():
            Notification.objects.create(
                destinataire=sec,
                message=f"Nouveau rendez-vous programmé entre {nom_patient} et Dr {nom_medecin} le {instance.date} à {instance.heure}.",
                lien=url,
                type="rendezvous"
            )
    else:
        # Notification de modification de statut/heure/date
        secretaires = Secretaire.objects.all()
        destinataires = list(set([patient, medecin]) | set(secretaires))
        for user in destinataires:
            # Format personnalisé pour chaque rôle
            if user == patient:
                message = f"Le statut de votre rendez-vous avec le Dr {nom_medecin} a été modifié à : {statut}."
            elif user == medecin:
                message = f"Le statut du rendez-vous avec le patient {nom_patient} a été modifié à : {statut}."
            else:
                message = f"Le statut du rendez-vous entre {nom_patient} et Dr {nom_medecin} a été modifié à : {statut}."

            # Évite les doublons exacts
            if not Notification.objects.filter(destinataire=user, message=message, type="rendezvous").exists():
                Notification.objects.create(
                    destinataire=user,
                    message=message,
                    lien=url,
                    type="rendezvous"
                )